# %%
import pandas as pd
import numpy as np
import sys, os
import h5py
from Variants_Preprocessor import Variants_Preprocessor
from vectorizer import vectorizer

# %%
# test for GWAS catalog data
# path and global variables specification
data_dir = "/home/bizon/Variants_Embedding/data"
counts_dir = "/home/bizon/CNN1d_modeling_pipeline/data/whole_genome_counts"
out_coor_dir = "/home/bizon/Variants_Embedding/variants_coordinates_data"
out_h5_dir = "/home/bizon/Variants_Embedding/variants_hdf5_data"
risk_gwas_fn = os.path.join(data_dir, "gwas_catalog_v1.0.2-associations_e100_r2020-10-20.tsv")
gnomad_all_gwas_fn = os.path.join(data_dir, "filtered.gnomad.liftover_grch38.tab.gz")
chrom_size_fn = os.path.join(data_dir, "chrom_size.csv")

assay_types = ["ATAC_seq", "DNase_seq", "Histone_Chipseq", "PolyA_RNAseq", "TF_ChIP_seq"]
study_accession = "GCST009524"
win_size = 100
win_num = 5

# %%
# load data to RAM
risk_gwas_df = pd.read_csv(risk_gwas_fn, sep='\t')
colnames = ['chrom', 'pos', 'ref', 'alt', 'rsid', 'AF', 'AC', 'vep']
gnomad_all_gwas_df = pd.read_csv(gnomad_all_gwas_fn, 
                                sep='\t',
                                compression='gzip',
                                names=colnames)

vp = Variants_Preprocessor(study_accession, 
                            chrom_size_fn, 
                            win_size=win_size,
                            win_num=win_num,
                            risk_gwas_df=risk_gwas_df, 
                            gnomad_all_gwas_df=gnomad_all_gwas_df,
                            out_coor_dir=out_coor_dir)
print(vp.selected_risk_gwas_df.head())

# match negative loci 
neg_variants_df = vp.match_k_negs(matching_interval_width=0.01, 
                                    kfolds=10, 
                                    seed=2020)
# write coordinates to the disk
out_coor_fn = vp.variants_coor_to_tsv()
print(f"coordinates file for counts fetching: {out_coor_fn}")
# %%
# use tabix to fetch features
cpg_feats_vectorizer = vectorizer(merged_counts_root_dir=counts_dir,
                                    assay_types=assay_types,
                                    meta_data_dir="/home/bizon/CNN1d_modeling_pipeline/data/filtered_metadata",
                                    win_size=win_size,
                                    win_num=win_num)
counts_features_arr = cpg_feats_vectorizer.vectorize_coor_file(out_coor_fn)
total_num_feats = counts_features_arr.shape[1]
print(f"fetched features with shape: {counts_features_arr.shape}")

# %%
# write fetched features to hdf5
out_h5_fn = os.path.join(out_h5_dir, f"{study_accession}.h5")
write_mode = "a" if os.path.exists(out_h5_fn) else "w"
if write_mode == "ａ":
    print("appending mode to: %s" % out_h5_fn)
elif write_mode == "w":
    print("writing mode to: %s" % out_h5_fn)
store = h5py.File(out_h5_fn, write_mode)
curr_row_ind = 0
coor_df = pd.read_csv(out_coor_fn, sep="\t", header=None)
coor_df.columns = ["chrom", "search_start", "search_end", "prev_win_num", "post_win_num", "variant_name"]
for ind, row in coor_df.iterrows():
    h5_key = row['variant_name']
    chrom, pos = h5_key.split('_')
    prev_win_num = row['prev_win_num']
    post_win_num = row['post_win_num']
    locus_corrsponding_row_num = row['prev_win_num'] + row['post_win_num'] + 1
    h5_value = counts_features_arr[curr_row_ind:(curr_row_ind+locus_corrsponding_row_num), :]
    if (prev_win_num < win_num):
        zero_placeholder_mat = np.zeros((win_num-prev_win_num, total_num_feats))
        h5_value = np.concatenate([zero_placeholder_mat, h5_value], axis=0)
    if (post_win_num < win_num):
        zero_placeholder_mat = np.zeros((win_num-post_win_num, total_num_feats))
        h5_value = np.concatenate([h5_value, zero_placeholder_mat], axis=0)
    h5_value = h5_value.T
    store['%s/counts_data' % h5_key] = h5_value #shape:(#features, seq_len)
    curr_row_ind = curr_row_ind + locus_corrsponding_row_num
store.close()
# %%
