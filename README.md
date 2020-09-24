# ENCODE(Encyclopedia of DNA Elements)
ENCODE experiments data processing 
#### Functionality:


#### Pipeline
1. Pre-processing metadata taken from ENCODE
- Usage:
  
```
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

- Audit Category:

    We followed the [data standard](https://www.encodeproject.org/data-standards/audits/) posted by ENCODE and decided to filter out all the data which has audit color as yellow and red. For example:
    - Extremely low read depth
    - Missing control alignments
    - inconsistent read counts
    - etc.
    
    This is the first step of filtering out the unqualified data using the internal filter of ENCODE, we can download the metadata using wget command. The following command is an example:
 ```
wget https://www.encodeproject.org/metadata/?type=Experiment&assay_title=ATAC-seq&assembly=GRCh38&files.file_type=bam&audit.NOT_COMPLIANT.category%21=unreplicated+experiment
```
   After download all the original metadata file from ENCODE, the metaprocessing.py script will continue filtering out unwanted data

- File status : Released
- File format: Bam File
- Assembly: GRCh38
- Alignments:
  - RNA Sequence: alignments
  - Histone_Chipseq: **Exclude** redacted unfiltered alignments & unfiltered alignments
  

    

2. Parse metadata
- Explanation: 

    This script is the preparation step. After running this script, Three folders will be created in the specified destination:
    - SeqTypes (For each SeqTypes)
        - Download
        - Processed
        - Merged
    - Download_urls： Generate csv files for each sequence type of the downloading url taken from the filtered_metadata from the previous step.
    - Logs

3. Submit Multiple Jobs into HPC

This script is the core part of our whole project, which will split the sequence into specified Window size (eg. 100) and generate the readcounts of the overlapping windows. This script  is highly dependent on which cluster we are using to complete the jobs. In our project, we are using [XSEDE Comet Cluster](https://portal.xsede.org/sdsc-comet), which uses SLURM to submit jobs. 

- Denpendencies:

  - test_single_bam_processing.sh
  - single_bam_file_processor.R :
    - Read in one bam file
    - Find the overlap with pre-defined windows
    - Output the readcounts to csv
    - Delete the bam file
   
- Usage:
```
python submit_multiple_jobs_single_exp_assay.py PolyA_RNAseq 100 --XSEDE_user_id xxx --resume_unfinished 
```

- Explanation:

    This script is designed to submit concurrent jobs without overloading the cluster but also efficiently process the data.
The main logic is as follows:

    


    
    
 







