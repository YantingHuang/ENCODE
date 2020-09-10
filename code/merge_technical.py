import sys
import argparse
import pandas as pd
import numpy as np

#ReadMe:
#eg: python merge_technical.py -i /Users/melanie/Desktop/ENCODE/metadata/filtered_metadata -c merged_read_counts.csv -o /Users/melanie/Desktop/ENCODE/merged_technical Histone_Chipseq
parser = argparse.ArgumentParser(description="Specify the type of sequence you want to merge")
parser.add_argument("seqname", help="choose from DNase_seq, Histone_Chipseq, PolyA_RNAseq,TF_Chipseq, ATAC_seq")
parser.add_argument("-i","--input",required=True,help="Path of the input metadata")
parser.add_argument("-c","--count",required=True,help="read counts you want to merge for technical replaictes")
parser.add_argument("-o","--output",required=True,help="Path of the output")
args=vars(parser.parse_args())
metaFile=args["input"]+'/'+'filtered_'+args["seqname"] +'_meta.csv'
countFile=args["count"]




#read in metadata and the count file 
meta = pd.read_csv(metaFile)
print(meta.shape)
df=pd.read_csv(countFile)
print(df.shape)

#check if there are any technical replicates we need to merge
technical_rep=meta['Technical replicate'].unique()
#if there is 1 in the technical replicates, that means there are technical replicates exist
if 1 in technical_rep:
	#store the original column num 
	original_column_num=len(df.columns)
	#create a dateframe of all the technical replicates
	mergeset=meta.loc[meta['Technical replicate']==1]
	#group by experiment accesion
	#technical replicates we want to merge shoule be belong to the same experiment!
	grouped_df=mergeset.groupby('Experiment accession')
	#create a 2D bam list to store bam file accessions belongs to each experiment
	bam_list=[]
	for key, item in grouped_df:
		bam_list.append(grouped_df.get_group(key)['File accession'].values)

	#create a variable to check for number of columns in the df we dropped
	filenum=0
	for i in range(len(bam_list)):
		file_accession=bam_list[i]
		new_name="_".join(file_accession)
		df[new_name]=df[file_accession].mean(axis=1)
		df.drop(file_accession,axis=1,inplace=True)
		filenum+=len(bam_list[i])  
	#check if our process yields to the correct column names 
	if(len(df.columns)!=original_column_num-filenum+len(bam_list)):
		print('false')
	print(df.shape)
	#output edited file 
	outputname = 'merge_technical_'+args["seqname"] +'_read_counts.csv'
	outputpath=args["output"]+'/'+outputname
	df.to_csv(outputpath, index = None, header=True)

else:
	print('No need to merge technical replicates because there are no technical replicates')





 

