#!/bin/bash
#SBATCH --job-name="single_bam_task_%j"
#SBATCH --output="/home/yanting/DL_based_functional_annotation/ENCODE/logs/PolyA_RNAseq/log_%j.out"
#SBATCH --error="/home/yanting/DL_based_functional_annotation/ENCODE/logs/PolyA_RNAseq/err_%j.out"
#SBATCH --partition=large-shared
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --export=ALL
#SBATCH --mem=300G
#SBATCH --time=12:00:00

#activate conda env
source /home/yanting/anaconda3/bin/activate research
#just for test purpose
which python
which Rscript

singleBamScript=/home/yanting/DL_based_functional_annotation/ENCODE/code/single_bam_file_processor.R

#downloadDir=/oasis/scratch/comet/yanting/temp_project/encode_data_processing/DNase_seq/download
#outputDir=/oasis/scratch/comet/yanting/temp_project/encode_data_processing/DNase_seq/processed
#bamURL=https://www.encodeproject.org/files/ENCFF878NHU/@@download/ENCFF878NHU.bam
#bamFn=ENCFF878NHU.bam
#wins100Fn=/home/yanting/DL_based_functional_annotation/ENCODE/commons/wins100.txt

#read from stdin
downloadDir=$1
outputDir=$2
bamURL=$3
bamFn=$4
wins100Fn=$5

echo $bamURL
echo $bamFn


#wget --directory-prefix $downloadDir $bamURL
Rscript $singleBamScript "${downloadDir}/${bamFn}" $wins100Fn $outputDir
