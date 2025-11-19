import sys
import os
from Bio import SeqIO
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

def create_specie(species_name, dataset_id):
# Create a record in species table
    sql = "INSERT INTO species (dataset_id, species_name) VALUES (%s, %s)"
    val = (dataset_id, species_name)
    cursor.execute(sql, val)

    db.commit()

def create_protein_record(species_id, fasta_info):
# Create a record in proteins table
    
    # Unpack list into variables
    uniprot_id, gene_id, eukprot_id, other_id, sequence, sequence_lenght, description = fasta_info

    sql = """
    INSERT INTO proteins 
    (species_id,uniprot_id,gene_id,eukprot_id,other_id,sequence,sequence_length,description)  
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        species_id,
        uniprot_id,
        gene_id,
        eukprot_id,
        other_id,
        sequence,
        sequence_lenght,
        description
        ))

    db.commit()

def get_fasta_info(fasta_record):
# Gather data from fasta header and sequence and returns them as a list
    
    uniprot_id = None
    gene_id = None
    eukprot_id = None
    other_id = None
    description = None

    if "|" in fasta_record.id:
        uniprot_id = fasta_record.id.split("|")[1]
        description = " ".join(fasta_record.description.split()[1:]).split("OS=")[0].strip()
    
    if "GN=" in fasta_record.description and "|" in fasta_record.id:
        gene_id = fasta_record.description.split("GN=")[1].split()[0]

    if fasta_record.id.startswith("EP"):
        eukprot_id = fasta_record.id

    sequence = str(fasta_record.seq)
    sequence_lenght = len(sequence)

    fasta_info = [uniprot_id, gene_id, eukprot_id, other_id, sequence, sequence_lenght, description]

    return fasta_info 

def get_specie_index():
# Return the index of the most recent species record

    cursor.execute("SELECT * FROM species ORDER BY species_id DESC LIMIT 1")

    results = cursor.fetchall()
    return results[0][0]

# ------------------------------
# MAIN
# ------------------------------

if len(sys.argv) < 4:
    print("Usage: python3.8 load_dataset.py <fasta_file> <specie_name> <dataset_id>")
    sys.exit(1)

fasta_file = sys.argv[1]
species_name = sys.argv[2]
dataset_id = sys.argv[3]

# Add specie to species table and get the newly generated species_id
create_specie(species_name, dataset_id)
species_id = get_specie_index()

# Iterate over fasta file and write each record into proteins table
for fasta_record in SeqIO.parse(fasta_file, "fasta"):
    fasta_info = get_fasta_info(fasta_record)
    create_protein_record(species_id, fasta_info)

cursor.close()
db.close()





