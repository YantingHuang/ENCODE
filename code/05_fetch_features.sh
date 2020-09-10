usage="$(basename "$0") [-o <out_file>] [-m <merged_counts_root_dir>] <in_file>

where:
    -h  show this help text
    -o  out tsv file (generated from input file name if not set)
    -m  the root directory of processed read counts of all assay types [default in Comet: /oasis/scratch/comet/yanting/temp_project/encode_data_processing]"

unset OPTARG
unset OPTIND

#Default variable
merged_counts_dir="/oasis/scratch/comet/yanting/temp_project/encode_data_processing"
in_file=""
out_file=""

#parse user input
while getopts ':ho:m:' opt; do
    case ${opt} in
        h) echo "$usage"
           exit
           ;;
        o) out_file=${OPTARG}
           ;;
        m) merged_counts_dir=${OPTARG}
           ;;
       \?) printf "illegal option: -%s\n" "$OPTARG" >&2
           echo "$usage" >&2
           exit 1
           ;;
    esac
done

shift $((OPTIND -1))

in_file=$1

if [ "$in_file" == "" ]
then
	echo "Required to provide a genomic coordinates tsv!"
	exit 1
fi

if [ "${in_file: -4}" != ".tsv" ]
then
	echo "The extension of input file must be .tsv!"
	exit 1
fi

file_name=$(basename $in_file)
name=${file_name%\.tsv*}
file_dir=$(dirname $in_file)

if [ "$out_file" == "" ]
then
    out_file=${file_dir}/${name}_fetched_features.tsv
fi

# Print General Information
echo "input coordinates file: $in_file"
echo "extracted feature will be stored in: $out_file"
echo "processed features stored in: $merged_counts_dir"
echo "Types of features to fetch: ${assay_types[@]}"

# can be modified
assay_types=(ATAC_seq DNase_seq Histone_Chipseq PolyA_RNAseq TF_ChIP_seq)

for assay_type in ${assay_types[@]};
	do
		merged_counts_fn=${merged_counts_dir}/${assay_type}/merged/${assay_type}_merged_counts.tsv.gz
		if [ -f ${merged_counts_fn} ]; 
		then
			echo "now fetching features from $merged_counts_fn"
			#output filename specification
			out_dir=$(dirname $in_file)
			features_fn=${out_dir}/tmp_features.txt
			header_fn=${out_dir}/header.txt
			coor_fn=${out_dir}/fetched_coor.tsv
			output_fn=${out_dir}/fetched_${assay_type}_out.tsv
			#fetch
			tabix -R $in_file $merged_counts_fn > $features_fn
			zless -S $merged_counts_fn | head -1 > $header_fn
			cat $header_fn $features_fn | cut -f 1,2,3 --complement > ${output_fn}
			cat $header_fn $features_fn | cut -f 1,2,3 > ${coor_fn}
			#remove intermediate files
			rm ${header_fn} ${features_fn}
			echo "completed"
		else
			echo "${merged_counts_fn} does NOT exist"
			exit 1
		fi
	done;
# combine all features (column-wise) to get the final output
paste "${coor_fn}" "${out_dir}"/fetched_*_out.tsv > "${out_file}"
rm "${out_dir}"/fetched_*_out.tsv
rm ${coor_fn}


