import pandas as pd
import sys, os

def create_data_dir_structure(seq_types, data_dir):
	for seq_type in seq_types:
		#create seq_type specific directory
		seq_dir = os.path.join(data_dir, seq_type)
		if not os.path.exists(seq_dir):
			os.mkdir(seq_dir)
		#create 2nd structure if necessary
		download_files_dir = os.path.join(seq_dir, "download")
		processed_files_dir = os.path.join(seq_dir, "processed")
		merged_files_dir = os.path.join(seq_dir, "merged")
		if not os.path.exists(download_files_dir):
			os.mkdir(download_files_dir)
		if not os.path.exists(processed_files_dir):
			os.mkdir(processed_files_dir)
		if not os.path.exists(merged_files_dir):
			os.mkdir(merged_files_dir)
	print("build data directory stuctures completed...")

def create_download_urls(seq_types, metadata_dir, urls_dir):
	if not os.path.exists(urls_dir):
		os.mkdir(urls_dir)
	for seq_type in seq_types: 
		meta_fn = os.path.join(metadata_dir, "filtered_%s_metadata.csv" %seq_type)
		meta_df = pd.read_csv(meta_fn)
		output_fn = os.path.join(urls_dir, "%s_urls.txt" % seq_type)
		meta_df["File download URL"].to_csv(output_fn, index=False)
		print(seq_type, meta_df.shape[0])

def create_log_dir(seq_types, log_dir):
	if not os.path.exists(log_dir):
		os.mkdir(log_dir)
	for seq_type in seq_types: 
		sub_log_dir = os.path.join(log_dir, seq_type)
		if not os.path.exists(sub_log_dir):
			os.mkdir(sub_log_dir)

local = False # local or COMET
if local:
	root_dir = "/Users/yantinghuang/Study/"
else:
	root_dir = "/home/yanting"
encode_dir = os.path.join(root_dir, "DL_based_functional_annotation/ENCODE")
if local:
	data_dir = os.path.join(encode_dir, "data")
else:
	#Comet 
	#data_dir = "/oasis/scratch/comet/yanting/temp_project/encode_data_processing"
	#Bridges
	data_dir = "/pylon5/eg4s89p/yanting/encode_data_processing/"
metadata_dir = os.path.join(encode_dir, "filtered_metadata")
urls_dir = os.path.join(encode_dir, "download_urls")
log_dir = os.path.join(encode_dir, "logs")
seq_types = ["ATAC_seq", "DNase_seq", "Histone_Chipseq", "PolyA_RNAseq", "TF_ChIP_seq", "WGBS"]

create_data_dir_structure(seq_types, data_dir)
create_download_urls(seq_types, metadata_dir, urls_dir)
create_log_dir(seq_types, log_dir)

