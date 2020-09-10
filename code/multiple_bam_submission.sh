#!/bin/bash
#SBATCH --job-name="log_driver"
#SBATCH --output=/home/yanting/DL_based_functional_annotation/ENCODE/logs/log_driver.out
#SBATCH --error=/home/yanting/DL_based_functional_annotation/ENCODE/logs/err_driver.out
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --export=ALL
#SBATCH --time=1-00:00

#activate conda env
source /home/yanting/anaconda3/bin/activate research

#run code
python /home/yanting/DL_based_functional_annotation/ENCODE/code/02_submit_multiple_jobs_single_exp_assay.py PolyA_RNAseq 100 --XSEDE_user_id yanting --resume_unfinished 
