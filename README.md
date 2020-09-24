# ENCODE(Encyclopedia of DNA Elements)
ENCODE experiments data processing 
#### Objective:


#### Environment:


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

- Dependencies:

  - test_single_bam_processing.sh
  - single_bam_file_processor.R :
    - Read in one bam file
    - Find the overlap with pre-defined windows
    - Output the readcounts to csv
    - Delete the bam file
  - Final_windows_size.py
   
- Usage:
```
python submit_multiple_jobs_single_exp_assay.py PolyA_RNAseq 100 --XSEDE_user_id xxx --resume_unfinished 
```
```
python Final_windows_size.py hg38.chrom.sizes 100 wins100.txt
```
- Explanation:

    This script is designed to submit concurrent jobs without overloading the cluster but also efficiently process the data.
The main logic is as follows:
    Keeping submitting jobs until we reach the maximum concurrent job number we specified in the argument(eg. 50 ), and then wait for 20 seconds and check if any jobs completed and we can submit the subsequent jobs.

4.  Generate the list of Technical Replicates

- Explanation:

    There are two types of replicates in the ENCODE database: biological replicates and technical replicates. Biological replicates are coming from two different biological samples while techinical replicates are coming from the same biological samples. So we decide to merge the readcounts for technical replicates of the sample experiment. 
    
    This script is used to generate the list of Technical Replicates that belong to the same Experiment Accession based on the filtered metadata we generated in the first step. 
    
5. Merge Processed Counts


    
    
    

    


    
    
 







