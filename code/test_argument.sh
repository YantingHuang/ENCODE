assay_types=(ATAC_seq DNase_seq Histone_Chipseq PolyA_RNAseq TF_ChIP_seq)
for assay_type in ${assay_types[@]};
	do
		merged_counts_fn="/Users/yantinghuang/Study/DL_based_functional_annotation/ENCODE/code/test_single_bam_processing.sh"
		if [ -f ${merged_counts_fn} ]; 
		then
			echo "hello"
		else
			echo "${merged_counts_fn} does NOT exist"
			exit 1
		fi
	done;
