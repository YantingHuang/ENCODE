import sys, os
import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="Specify the type of sequence you want to merge")
parser.add_argument("seqname", help="choose from DNase_seq, Histone_Chipseq, PolyA_RNAseq, TF_ChIP_seq, ATAC_seq")
parser.add_argument("-i","--input_dir",required=True,help="directory that contains metadata")
parser.add_argument("-o","--output_dir",required=True,help="directory for the output")
args=vars(parser.parse_args())

metaFile = os.path.join(args["input_dir"], 'filtered_'+args["seqname"] +'_metadata.csv')

#read in metadata and the count file 
meta = pd.read_csv(metaFile)
print(meta.shape)

#check if there are any technical replicates we need to merge
technical_rep = meta['Technical replicate'].unique()

#if there is 1 in the technical replicates, that means there are technical replicates exist
if 1 in technical_rep:
	#create a dateframe of all the technical replicates
	mergeset = meta.loc[meta['Technical replicate']==1]
	# group by experiment accesion
	# technical replicates we want to merge should belong to the same experiment!
	grouped_df = mergeset.groupby('Experiment accession')
	#create a 2D bam list to store bam file accessions belongs to each experiment
	bam_list=[]
	for key, item in grouped_df:
		bam_list.append(';'.join(grouped_df.get_group(key)['File accession'].values.tolist()))
	bam_ser = pd.Series(bam_list)
	bam_ser.name= "merge_list"

	#output edited file 
	output_fn = args["seqname"] +'_tech_replicates.csv'
	output_fn = os.path.join(args["output_dir"], output_fn)
	bam_ser.to_csv(output_fn, index=False, header=True)
else:
	print('No need to merge technical replicates because there are no technical replicates')





 

