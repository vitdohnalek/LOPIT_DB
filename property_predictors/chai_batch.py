#Predict 3D structure of a protein from aminoacid sequence using Chai-1 model
#Input is a fasta file containing either one or multiple aminoacid sequences
#Output is a .cif file for each sequence

from pathlib import Path

import numpy as np
import torch
import os
from Bio import SeqIO
from Bio import PDB
import numpy as np
import glob
from chai_lab.chai1 import run_inference


#computes average pLDDT for a cif file
def compute_plddt(cif_path):

    parser = PDB.MMCIFParser(QUIET=True)
    structure = parser.get_structure("structure", cif_path)
    
    plddt_scores = []
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    plddt_scores.append(atom.bfactor)
    
    if plddt_scores:
        avg_plddt = np.mean(plddt_scores)
        return avg_plddt
    else:
        print("No pLDDT scores found in the CIF file.")
        return None

#Write fasta file into tmp
def prepare_input(seq_ID, sequence):
    fasta = f">protein|name={seq_ID}\n{sequence}"

    fasta_path = Path(f"./tmp/{seq_ID}.fasta")
    fasta_path.write_text(fasta)

#Predict 3D protein structure
def prediction(seq_ID):

    fasta_path = Path(f"./tmp/{seq_ID}.fasta")
    output_dir = Path("./tmp/outputs")

    candidates = run_inference(
        fasta_file=fasta_path,
        output_dir=output_dir,
        # 'default' setup
        num_trunk_recycles=3,
        num_diffn_timesteps=200,
        seed=42,
        device=torch.device("cuda:0"),
        use_esm_embeddings=True,
    )

    cif_paths = candidates.cif_paths
    scores = [rd.aggregate_score for rd in candidates.ranking_data]

    # Load pTM, ipTM, pLDDTs and clash scores for sample 2
    #scores = np.load(output_dir.joinpath("scores.model_idx_2.npz"))

#Predict structures for multiple proteins from fasta file
def batch_chai(fasta_file):
    for seq_rec in SeqIO.parse(fasta_file, "fasta"):
        seq_ID = str(seq_rec.id)
        sequence = str(seq_rec.seq)

        #prepare fasta file for chai
        prepare_input(seq_ID, sequence)
        print("Data prepared..")

        #Run chai
        prediction(seq_ID)

        print(f"prediction done for {seq_ID}..")
        
        #Picks the best model based on pLDDT value
        best_model = ""
        best_plddt = 0

        #finds model with highest pLDDT value
        for cif_file in glob.glob("./tmp/outputs/pred.model_idx_*.cif"):
            model_number = cif_file.split("_idx_")[-1][:-4]
            plddt = compute_plddt(cif_file)
            if plddt > best_plddt:
                best_plddt = plddt
                best_model = model_number
        print(f"best model {best_model} has {best_plddt} pLDDT.. ")

        #Rename best structure and its scores
        #Cleanup
        os.system(f"mv ./tmp/outputs/pred.model_idx_{best_model}.cif ./tmp/outputs/{seq_ID}.cif")
        os.system(f"mv ./tmp/outputs/scores.model_idx_{best_model}.npz ./tmp/outputs/{seq_ID}.npz")
        os.system(f"rm ./tmp/outputs/pred.model_idx_*.cif")
        os.system(f"rm ./tmp/outputs/scores.model_idx_*.npz")

os.system("mkdir ./tmp/")
os.system("mkdir ./tmp/outputs/")
batch_chai("FASTA_FILE")
