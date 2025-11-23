import csv
import sys
import os
import mysql.connector


# ------------------------------
# DB CONFIG VIA ENV VARIABLES
# ------------------------------

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "lopit_db")

if DB_PASS is None:
    raise RuntimeError("Environment variable DB_PASS is required but not set.")

# Connect to the database
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
)

cursor = db.cursor()


# ------------------------------
# FUNCTIONS
# ------------------------------

def find_protein_id(uniprot_id, gene_id):
    #Find protein_id by UniProt or gene_id (priority: UniProt)

    # Try UniProt first
    if uniprot_id not in ("", None, "None"):
        cursor.execute("SELECT protein_id FROM proteins WHERE uniprot_id = %s", (uniprot_id,))
        row = cursor.fetchone()
        if row:
            return row[0]

    # Try gene_id second
    if gene_id not in ("", None, "None"):
        cursor.execute("SELECT protein_id FROM proteins WHERE gene_id = %s", (gene_id,))
        row = cursor.fetchone()
        if row:
            return row[0]

    return None


def insert_foldseek_record(protein_id, row, structure_predictor):
    #Insert a row into foldseek table

    sql = """
    INSERT INTO foldseek (
        protein_id,
        structure_predictor,
        plddt,
        db_swiss,
        db_uniprot,
        db_proteomes,
        most_frequent_hit,
        most_frequent_hit_n
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        protein_id,
        structure_predictor,
        float(row["pLDDT"]),
        row["Swiss-Prot"] or None,
        row["UniProt"] or None,
        row["AlphaFold-Proteomes"] or None,
        row["Most frequent hit"] or None,
        int(row["Most frequent hit n"])
    )

    cursor.execute(sql, values)
    db.commit()


# ------------------------------
# MAIN
# ------------------------------

if len(sys.argv) < 3:
    print("Usage: python3 load_foldseek.py <foldseek_results.tsv> <structure_predictor>")
    sys.exit(1)

tsv_file = sys.argv[1]
structure_predictor = sys.argv[2]

with open(tsv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        uniprot_id = row["UniProt ID"].strip()
        gene_id = row["Gene"].strip()

        protein_id = find_protein_id(uniprot_id, gene_id)

        if protein_id is None:
            print(f"No protein found for UniProt={uniprot_id}, Gene={gene_id}")
            continue

        try:
            insert_foldseek_record(protein_id, row, structure_predictor)
            print(f"Inserted foldseek row for protein_id={protein_id}")
        except mysql.connector.errors.IntegrityError:
            print(f"Foldseek entry already exists for protein_id={protein_id}, skipping")

cursor.close()
db.close()
