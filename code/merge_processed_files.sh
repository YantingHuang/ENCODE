#!/bin/bash
#SBATCH --job-name="merge_counts"
#SBATCH --output="/home/yanting/DL_based_functional_annotation/ENCODE/logs/log_merge_counts.out"
#SBATCH --error="/home/yanting/DL_based_functional_annotation/ENCODE/logs/err_merge_counts.out"
#SBATCH --partition=large-shared
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem=900G
#SBATCH --export=ALL
#SBATCH --time=12:00:00
#needed for Comet: SBATCH -A unb111
#SBATCH -A unb111

#Comet partitions: compute, large-shared
#Bridges partitions: RM, RM-shared, RM-small, LM
#assay type supported: "ATAC_seq", "DNase_seq", "Histone_Chipseq", "PolyA_RNAseq", "TF_ChIP_seq", "WGBS"
#activate conda env
source /home/yanting/anaconda3/bin/activate research

assay_type="TF_ChIP_seq"
#Comet
root_dir="/oasis/scratch/comet/yanting/temp_project/encode_data_processing/$assay_type"
#Bridges
#root_dir="/pylon5/eg4s89p/yanting/encode_data_processing/$assay_type"
tech_rep_lst_dir="/home/yanting/DL_based_functional_annotation/ENCODE/technique_rep_merge_accessions"

echo $root_dir

Rscript /home/yanting/DL_based_functional_annotation/ENCODE/code/04_merge_processed_counts.R $root_dir $assay_type $tech_rep_lst_dir