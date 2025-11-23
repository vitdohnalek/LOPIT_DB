-- 1. Create and select database
CREATE DATABASE IF NOT EXISTS lopit_db;
USE lopit_db;

-- 2. Create table of species included in the LOPIT project
CREATE TABLE species (
	species_id INT AUTO_INCREMENT PRIMARY KEY,
	dataset_id VARCHAR(255) NOT NULL,
	species_name VARCHAR(255) NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create table of proteins
-- Contains different protein and gene IDs and seqeunces
CREATE TABLE proteins (
	protein_id INT AUTO_INCREMENT PRIMARY KEY,
	species_id INT NOT NULL,
	uniprot_id VARCHAR(30),
	gene_id VARCHAR(255),
	eukprot_id VARCHAR(255),
	other_id VARCHAR(255),
	sequence MEDIUMTEXT NOT NULL,
	sequence_length INT NOT NULL,
	description TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	-- Uniqueness constraints
	UNIQUE (uniprot_id),
	UNIQUE (eukprot_id),
	UNIQUE (species_id, gene_id),

	FOREIGN KEY (species_id) REFERENCES species(species_id) ON DELETE CASCADE
);

-- 4. Create table of foldseek annotations
-- Contains top hits against three databases and the most frequent hit in the results
CREATE TABLE foldseek (
	protein_id INT PRIMARY KEY,
	structure_predictor VARCHAR(255),
	plddt FLOAT,
	db_swiss VARCHAR(255),
	db_uniprot VARCHAR(255),
	db_proteomes VARCHAR(255),
	most_frequent_hit VARCHAR(255),
	most_frequent_hit_n INT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (protein_id) REFERENCES proteins(protein_id) ON DELETE CASCADE
);
