import subprocess
import pandas as pd
import numpy as np 
import sys, os

class vectorizer(object):
    """The vectorizer which can convert from a single genomic coordinate to a feature matrix"""
    def __init__(self,
                merged_counts_root_dir, 
                assay_types, 
                meta_data_dir=None, 
                win_size=100, 
                win_num=5):
        """
        Args:
            merged_counts_root_dir (str): a string that indicates the root dir of merged counts
            assay_types (list): a list of all desired assay names
            win_size (int): the length of a single window. Default: 100
            win_num (int): the number of consecutive windows to include in the model (one side)
        """

        self.merged_counts_root_dir = merged_counts_root_dir
        self.assay_types = assay_types
        self.meta_data_dir = meta_data_dir
        self.win_size = win_size
        self.win_num = win_num

    def vectorize_single_coor(self, center_pos_coor):
        """ fetch features for a single locus
        Args:
            center_pos_coor (str): a string to indicate the coordinate of the center e.g.: "chr16:53434200"
        Returns:
            all_fetched_feats_mat (numpy.ndarray) of shape: (2*win_size + 1, num_features)
        """
        chrom, pos = center_pos_coor.split(":")
        start_pos = int(pos) - self.win_size * self.win_num
        end_pos   = int(pos) + self.win_size * self.win_num + 1
        position_query = f"{chrom}:{start_pos:d}-{end_pos:d}"
        print(f"fetching features for {position_query}")
        all_fetched_feats_mat = []
        for assay_type in self.assay_types:
            merged_counts_fn = os.path.join(self.merged_counts_root_dir, f"{assay_type}_merged_counts.tsv.gz")
            out = subprocess.Popen(['tabix', merged_counts_fn, position_query], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)
            stdout, _ = out.communicate()
            stdout = stdout.decode("utf-8").strip('\n') 
            fetch_feats_array = pd.DataFrame(([single_win_features.split('\t') 
                                            for single_win_features in stdout.split('\n')]))
            fetch_feats_array = fetch_feats_array.iloc[:, 3:].values.astype('float32')
            all_fetched_feats_mat.append(fetch_feats_array)
        all_fetched_feats_mat = np.concatenate(all_fetched_feats_mat, axis=1)
        return all_fetched_feats_mat
	
    def vectorize_coor_file(self, coor_for_search_fn):
        """ fetch features for multiple loci/region included in the tab-delimited file
        Args:
            coor_for_search_fn (str): the file name of the searching query for "tabix -R" batch query
        Returns:
            all_fetched_feats_mat (numpy.ndarray) of shape: (2 * win_size + 1, num_features)
        """
        all_fetched_feats_mat = []
        for assay_type in self.assay_types:
            merged_counts_fn = os.path.join(self.merged_counts_root_dir, f"{assay_type}_merged_counts.tsv.gz")
            out = subprocess.Popen(['tabix', merged_counts_fn, "-R", coor_for_search_fn], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)
            stdout, _ = out.communicate()
            stdout = stdout.decode("utf-8").strip('\n') 
            fetch_feats_array = pd.DataFrame(([single_assay_features.split('\t') 
                                                for single_assay_features in stdout.split('\n')]))
            fetch_feats_array = fetch_feats_array.iloc[:, 3:].values.astype('float32')
            all_fetched_feats_mat.append(fetch_feats_array)
        all_fetched_feats_mat = np.concatenate(all_fetched_feats_mat, axis=1)
        return all_fetched_feats_mat
