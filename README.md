# ENCODE(Encyclopedia of DNA Elements)
ENCODE experiments data processing 
#### Pipeline
1. Pre-processing metadata taken from ENCODE\
- Usage:
  
```angular2
python metaprocessing.py -i /Users/melanie/Desktop/ENCODE/metadata -o /Users/melanie/Desktop/ENCODE/metadata/filtered_metadata Histone_Chipseq
```
 
 Arguments:  
  
  -i:  Specify the path of the original metadata (taken directly from ENCODE) folder\
  -o:  Specify the path of the output filtered metadata\
  Last argument to choose from:
  1. DNase_seq
  2. Histone_Chipseq
  3. PolyA_RNAseq
  4. TF_Chipseq,WGBS
  5. ATAC_seq
- Explanation:

The original metadata txt file are download from the ENCODE official website following the below mentioned criteria:
1. Audit Category：\
    We followed the [data standard](https://www.encodeproject.org/data-standards/audits/) posted by ENCODE and decided to filter out all the data which has audit color as yellow and red. For example:
    - Extremely low read depth
    - Missing control alignments
    - inconsistent read counts
    - etc.
    