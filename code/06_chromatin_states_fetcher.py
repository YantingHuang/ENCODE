import numpy as np
import tabix

def fetch_chromatin_states(tb_handfile, chrom, pos, win_num, win_size=100, num_chrom_states=15):
	"""input a 1-based coordinates and search chromatin states in the 0-based bed file"""
	pos = int(pos)
	one_hot_encoded_arr = np.zeros((num_chrom_states, 2*win_num+1)).astype(int)
	search_start_0based = pos - win_num*win_size -1
	search_end_0based = pos + win_num*win_size

	win_stop_points = list(range((search_start_0based//100+1)*100, search_end_0based, win_size))
	win_ends = win_stop_points + [search_end_0based]
	win_starts = [search_start_0based] + win_stop_points
	search_wins = list(zip(win_starts, win_ends))
	for win_ind, search_win in enumerate(search_wins):
		query_result = list(tb.query(chrom, search_win[0], search_win[1]))
		if len(query_result)==0:
			continue
		else:
			for win_res in query_result:
				one_hot_encoded_arr[int(win_res[-1])-1, win_ind] = 1
	print(one_hot_encoded_arr)
	print(one_hot_encoded_arr.shape)


chrom_matrin_states_fn = "/Users/yantinghuang/Study/DL_based_functional_annotation/ENCODE/data/chromatin_states_hg38/E001_15_coreMarks_hg38lift_stateno.bed.gz"
tb = tabix.open(chrom_matrin_states_fn)
fetch_chromatin_states(tb, 'chr1', 779821, win_num=2)