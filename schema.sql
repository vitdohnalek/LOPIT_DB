-- 1. Create and select database
CREATE DATABASE IF NOT EXISTS lopit_db;
USE lopit_db;

-- 2. Create table of species included in the LOPIT project
CREATE TABLE species (
	species_id INT AUTO_INCREMENT PRIMARY KEY,
	dataset_id VARCHAR(255) NOT NULL,
	species_name VARCHAR(255) NOT NULL	
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

	-- Uniqueness constraints
	UNIQUE (uniprot_id),
	UNIQUE (eukprot_id),
	UNIQUE (species_id, gene_id),

	FOREIGN KEY (species_id) REFERENCES species(species_id)
);


