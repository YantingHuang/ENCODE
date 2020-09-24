import sys
import argparse
import pandas as pd
import numpy as np

#ReadMe:
#eg: python metaprocessing.py -i /Users/melanie/Desktop/ENCODE/metadata -o /Users/melanie/Desktop/ENCODE/metadata/filtered_metadata Histone_Chipseq
parser = argparse.ArgumentParser(description="Specify the type of sequence you want to process")
parser.add_argument("seqname", help="choose from DNase_seq, Histone_Chipseq, PolyA_RNAseq,TF_Chipseq,WGBS, ATAC_seq")
parser.add_argument("-i","--input",required=True,help="Path of the input metadata")
parser.add_argument("-o","--output",required=True,help="Path of the output filtered metadata")
args=vars(parser.parse_args())
Filename=args["input"]+'/'+args["seqname"] +'_meta.txt'


#Filename=sys.argv[1]
df = pd.read_csv(Filename, sep="\t")#argument

if "RNAseq" in args["seqname"]:
	df= df[(df['Assembly']=='GRCh38')& (df['File format']=='bam')&(df['File Status']=='released')&(df['Output type']=='alignments')]
	outputname = 'filtered_'+args["seqname"] +'_meta.csv'
	outputpath=args["output"]+'/'+outputname
	df.to_csv(outputpath, index = None, header=True)
	#print(df['Assembly'].value_counts())

elif "Histone_Chipseq" in args["seqname"]:
	#df['Output type'].value_counts()
	#alignments                        1559
	#redacted unfiltered alignments     228
	#redacted alignments                228
	#we can see redacted unfiltered alignments is paired with redacted alighnments, so we keep redacted alignments
	df= df[(df['Assembly']=='GRCh38')& (df['File format']=='bam')&(df['File Status']=='released')&(df['Output type']!='redacted unfiltered alignments')&(df['Output type']!='unfiltered alignments')]
	outputname = 'filtered_'+args["seqname"] +'_meta.csv'
	outputpath=args["output"]+'/'+outputname
	df.to_csv(outputpath, index = None, header=True)
else:

#TFseqmeta
#underscore split
#sequecing type 
# if RNAseq: df['transcriptome']
# if not : regular

#150

	df= df[(df['Assembly']=='GRCh38')& (df['File format']=='bam')&(df['File Status']=='released')&(df['Output type']!='unfiltered alignments')]
	outputname = 'filtered_'+args["seqname"] +'_meta.csv'
	outputpath=args["output"]+'/'+outputname
	df.to_csv(outputpath, index = None, header=True)
	 #formatted string

