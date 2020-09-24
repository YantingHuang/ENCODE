
#use python Final_windows_size.py input_chromosomesize_file windowsize outputfile 
#python Final_windows_size.py hg38.chrom.sizes 100 wins100.txt

import sys
import pandas as pd
import numpy as np
inputs = sys.argv
column_names=['chromosome','length']
hg38_length = pd.read_csv(inputs[1], delim_whitespace=True, names=column_names, header=None,index_col=None)
allChr=['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9',  'chr10','chr11', 'chr12', 'chr13', 'chr14',
       'chr15', 'chr16', 'chr17', 'chr18', 'chr19','chr20', 'chr21', 'chr22',  'chrX','chrY']
winsize=int(inputs[2])
results = pd.DataFrame(columns =['seqnames','start', 'end'])
for chromosome in allChr:
    lengthOfChro=hg38_length.length[hg38_length.chromosome==chromosome].item()
    chrEnd = list(range(winsize, lengthOfChro+1, winsize))
    if(lengthOfChro%winsize!=0):
        chrEnd.append(lengthOfChro)
        chrStart= list(range(1, (chrEnd[-1]//winsize)*winsize+2, winsize))
    else:
        chrStart = list(range(1, chrEnd[-1]-98, winsize))
    
    seqnames = [chromosome]*len(chrEnd)
    df = pd.DataFrame(list(zip(seqnames,chrStart, chrEnd)), 
               columns =['seqnames','start', 'end']) 
    outputfile=inputs[3]
    results=results.append(df,ignore_index = True)
results.to_csv(outputfile, sep='\t',index=False)



