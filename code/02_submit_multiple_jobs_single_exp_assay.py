import argparse
import sys, os
import pandas as pd 
import subprocess
import datetime
import time

parser = argparse.ArgumentParser(prog="submit_multiple_slurm_jobs_simutaneously", description="submit multiple slurm jobs in the same time")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('seq_assay_type', help='choose one from ATAC_seq/DNase_seq/Histone_Chipseq/PolyA_RNAseq/TF_ChIP_seq', choices=["ATAC_seq", "DNase_seq", "Histone_Chipseq", "PolyA_RNAseq", "TF_ChIP_seq"])
parser.add_argument('maximum_concurrent_jobs', type=int, help='maximum number of concurrent slurm jobs')
parser.add_argument('--run_first_N_jobs', type=int, help='only downloading and processing first N urls (testing purpose)', default=None)
parser.add_argument('--XSEDE_user_id', help='user id for checking job status', default="yanting")
parser.add_argument('--resume_unfinished', action='store_true', help="resume finishing uncompleted jobs when unexpected condition occurs")

args = parser.parse_args()
#args = parser.parse_args(['DNase_seq', '5', '--run_first_N_jobs', '20', '--resume_unfinished'])
#parser.print_help()

def submit_single_bam_processing_job(url_series, curr_job_index, download_dir, processed_dir, wins100_fn, total_num_jobs):
	bam_URL = url_series.iloc[curr_job_index]
	bam_name = "%s.bam" % bam_URL.strip('.bam').split('/')[-1]
	single_bam_submission_sh = "/home/yanting/DL_based_functional_annotation/ENCODE/code/test_single_bam_processing.sh"
	single_bam_submission_cmd = ["sbatch", single_bam_submission_sh, download_dir, processed_dir, bam_URL, bam_name, wins100_fn]
	sbatch_process = subprocess.Popen(single_bam_submission_cmd,
						stdout=subprocess.PIPE, 
						stderr=subprocess.PIPE)
	current_time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	print("job %i/%i submitted at %s" % (curr_job_index+1, total_num_jobs, current_time), flush=True)
	curr_job_index += 1
	return curr_job_index

def generate_unfinished_bam_urls(download_dir, processed_dir, download_urls_df):
	unfinished_bam_download_lst = os.listdir(download_dir)
	processed_lst = [bam.split('.')[0] for bam in os.listdir(processed_dir)]
	download_urls_df['bam_name'] = download_urls_df['File download URL'].str.rsplit('/', n=1, expand=True)[1]

	check_downloaded_condition = download_urls_df['bam_name'].isin(unfinished_bam_download_lst)
	check_processed_condition = ~download_urls_df['bam_name'].str.split('.', expand=True)[0].isin(processed_lst)
	# unfinished urls is comprised of two parts
	# 1) the jobs are submitted and finish downloading procedure but have not finished
	# 2) the jobs that are never submitted / downloading process not completed
	unfinished_df = download_urls_df[check_downloaded_condition | check_processed_condition]
	# delete all files existing in download directory
	#for downloaded_bam in unfinished_bam_download_lst:
	#	abs_path_bam = os.path.join(download_dir, downloaded_bam)
	#	os.remove(abs_path_bam)
	#	print("%s removed" % abs_path_bam)
	return unfinished_df

print("Processing data for assay %s" % args.seq_assay_type)
download_urls_dir = "/home/yanting/DL_based_functional_annotation/ENCODE/download_urls"
scratch_dir = "/oasis/scratch/comet/yanting/temp_project/encode_data_processing"
download_dir = os.path.join(scratch_dir, "%s/download" % args.seq_assay_type)
processed_dir = os.path.join(scratch_dir, "%s/processed" % args.seq_assay_type)

wins100_fn = "/home/yanting/DL_based_functional_annotation/ENCODE/commons/wins100.txt"
download_urls_fn = os.path.join(download_urls_dir, "%s_urls.txt"%args.seq_assay_type)

download_urls_df = pd.read_csv(download_urls_fn)

if args.resume_unfinished:
	print("resume unfinished jobs instead of do all jobs from scratch...")
	download_urls_df = generate_unfinished_bam_urls(download_dir, processed_dir, download_urls_df)

if args.run_first_N_jobs:
	print("process the first %i files for testing..."%args.run_first_N_jobs, flush=True)
	download_urls_df = download_urls_df.iloc[:args.run_first_N_jobs]

curr_job_index = 0
total_num_jobs = len(download_urls_df['File download URL'])
print("total number of bams: %i" % total_num_jobs, flush=True)
while curr_job_index <= (total_num_jobs-1):
	if curr_job_index!=0:
		time.sleep(20)
	squeue_cmd = ["squeue", "-u", args.XSEDE_user_id]
	squeue_process = subprocess.Popen(squeue_cmd,
						stdout=subprocess.PIPE, 
						stderr=subprocess.PIPE)
	stdout, stderr = squeue_process.communicate()
	stdout = stdout.decode('utf-8')
	num_curr_running_task = stdout.count(args.XSEDE_user_id) - 1 #needs to exclude the running driver program 
	if num_curr_running_task < args.maximum_concurrent_jobs:
		num_tasks_to_submit = args.maximum_concurrent_jobs - num_curr_running_task
		for _ in range(num_tasks_to_submit):
			if (curr_job_index <= (total_num_jobs-1)): #do NOT submit job if curr_job_index reaches the total num of tasks
				curr_job_index = submit_single_bam_processing_job(download_urls_df['File download URL'], 
																	curr_job_index, 
																	download_dir, processed_dir, 
																	wins100_fn, total_num_jobs)
			else:
				break


