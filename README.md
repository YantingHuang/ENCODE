# ENCODE (Encyclopedia of DNA Elements)
ENCODE experiments data processing 
#### Objective:
ENCODE (Encyclopedia of DNA Elements) contains omics profiles obtained across multiple experiment assays. In this project, we preprocess around 6,100 alignment profiles from DNase sequencing, histone ChIP-seq, TF ChIP-seq, PolyA RNA-seq and ATAC-seq to obtain their read counts coverage across the whole human genome in the form of around 30 million predefined 100-bp bins. This repo contains the whole pipeline of data processing starting from preprocessing the ENCODE experiments meta data to fetching the counts data for the genomic location of interests (with a GWAS example using GWAS Catlog disease-related risky variants) in batch. The user can replicate the data processing pipeline for the new experiments added to ENCODE or other experiments assays of interest in the future.

The full processed data in .tsv.gz format and their indexing files will be available in [TODO].

#### Prerequisites:
Software:
- Python  3.7.9
- R 3.5.1
- tabix 1.7-2
- bgzip 1.7-2

Packages:
- numpy 1.19.2
- pandas 0.25.3
- h5py 2.10.0
- GenomicRanges 1.34.0
- GenomicAlignments 1.18.1
- data.table 1.12.8

#### Pipeline
00. Pre-processing metadata taken from ENCODE
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
  

    

01. Parse metadata
- Explanation: 

    This script is the preparation step. After running this script, Three folders will be created in the specified destination:
    - SeqTypes (For each SeqTypes)
        - Download
        - Processed
        - Merged
    - Download_urls： Generate csv files for each sequence type of the downloading url taken from the filtered_metadata from the previous step.
    - Logs

02. Submit Multiple Jobs into HPC

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

03.  Generate the list of Technical Replicates

- Explanation:

    There are two types of replicates in the ENCODE database: biological replicates and technical replicates. Biological replicates are coming from two different biological samples while techinical replicates are coming from the same biological samples. So we decide to merge the readcounts for technical replicates of the sample experiment. 
    
    This script is used to generate the list of Technical Replicates that belong to the same Experiment Accession based on the filtered metadata we generated in the first step. 
    
04. Merge Processed Counts
- Usage:
```
Rscript 04_merge_processed_counts.R root_dir assay_type tech_rep_lst_dir
```
- Explanation:
  
  Merge Technical replicates based on the list generated in step 03. The merging is based on the mean read counts. A tab-delimited file and a fst file (can only be read by R) will be generated.

05. Fetch counts data of interests
- Usage:
```
python 05_fetch_gwas_variants_features.py
```
- Explanation:
  We provided an example of efficient counts data fetching procedure here. First, we process the GWAS catalog risky variants and match neutral variants based on AF and genomic context from gnomAD database. A coordinate file is generated after that and will be used for the counts data fetching procedure. Next, a Vectorizer() object is initialized and internally uses tabix to fetch the regions of interest in batch. (Note: multiple adjacent regions fetching is supported, i.e., fetch counts features for not only the center variant window but also its up- and downstream windows). At last, the fetched features will be written to a hdf5 file and the keys are in the form of "[variant_name]/counts_data".

  To fit your own purposes, you can generate the coordinates to search tab-delimited file as shown in "example_data/GCST007038_variants.tsv". The columns correspond to 1) chromosome, 2) search start, 3) search end, 4) number of upstream windows, 5) number of downstream windows and genomic coordinate of the center location, respectively. Note that the search start is inclusive and the search end is exclusive, i.e., [start, end). The Vectorizer() object takes the tab-delimited file as input for the further data fetching procedure.
  



    

    
    
    

    


    
    
 







