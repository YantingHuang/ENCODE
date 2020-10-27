# %% 
import pandas as pd
import numpy as np
import sys, os
# %% 
class Variants_Preprocessor:
    def __init__(self, 
                study_accession, 
                ucsc_chrom_len_fn,
                win_size=100,
                win_num=5,
                risk_gwas_df=None, 
                gnomad_all_gwas_df=None, 
                risk_gwas_fn=None, 
                gnomad_all_gwas_fn=None,
                out_coor_dir="."):
        self.study_accession = study_accession
        self.chrom_length_fn = ucsc_chrom_len_fn
        self.win_size = win_size
        self.win_num = win_num
        self.out_coor_dir=out_coor_dir
        self.pos_variants_df = None
        self.neg_variants_df = None
        print(f"coordinates file will be written to {self.out_coor_dir}")
        if risk_gwas_df is not None:
            print("load from RAM")
            self.risk_gwas_df = risk_gwas_df.copy()
        elif risk_gwas_fn is not None:
            print(f"loading {risk_gwas_fn}...")
            self.risk_gwas_df = pd.read_csv(risk_gwas_fn, sep='\t')
        else:
            raise ValueError("require risk variants dataframe or file path")
        if gnomad_all_gwas_df is not None:
            print("load from RAM")
            self.gnomad_all_gwas_df = gnomad_all_gwas_df.copy()
        elif gnomad_all_gwas_fn is not None:
            print(f"loading {gnomad_all_gwas_fn}...")
            colnames = ['chrom', 'pos', 'ref', 'alt', 'rsid', 'AF', 'AC', 'vep']
            self.gnomad_all_gwas_df = pd.read_csv(gnomad_all_gwas_fn, 
                                                    sep='\t',
                                                    compression='gzip',
                                                    names=colnames)
        else:
            raise ValueError("require gnomad filtered gnomad variants dataframe or file path")
        valid_chroms = [f"chr{i}" for i in range(1, 23)] + ['chrX']
        self.gnomad_all_gwas_df = self.gnomad_all_gwas_df.loc[self.gnomad_all_gwas_df.chrom.isin(valid_chroms)]
        self.gnomad_all_gwas_df.loc[:, 'genomic_region'] = [vep.split("|")[1] 
                                                            for vep in self.gnomad_all_gwas_df.vep]
        self.selected_risk_gwas_df = self._generate_selected_risk_variants_df()
        self.gnomad_all_gwas_df.drop(['ref', 'alt', 'AC', 'vep'], axis=1, inplace=True)

    def match_k_negs(self, matching_interval_width=0.01, kfolds=10, seed=2020):
        all_neg_variants = []
        valid_pos_ind = []
        gnomad_pos_gwas_df = self.gnomad_all_gwas_df[self.gnomad_all_gwas_df.rsid.isin(self.selected_risk_gwas_df.SNP_ID_CURRENT)]
        gnomad_neg_gwas_df = self.gnomad_all_gwas_df[~self.gnomad_all_gwas_df.rsid.isin(self.selected_risk_gwas_df.SNP_ID_CURRENT)]
        processed_count = 0
        for _, row in self.selected_risk_gwas_df.iterrows():
            if (processed_count%10 == 0):
                print(processed_count)
            rs_id = row['SNP_ID_CURRENT']
            gnomad_record = gnomad_pos_gwas_df.loc[gnomad_pos_gwas_df.rsid==rs_id, 'AF']
            af = gnomad_record.item()
            pos_ind = gnomad_record.index.item()
            low = max(af - matching_interval_width, 0.0)
            high = min(af + matching_interval_width, 1.0)
            context = row['CONTEXT']
            filtered_df = gnomad_neg_gwas_df[(gnomad_neg_gwas_df.AF>low) & 
                                            (gnomad_neg_gwas_df.AF<high) &
                                            (gnomad_neg_gwas_df.genomic_region == context)]
            num_matched_variants = filtered_df.shape[0]
            if (num_matched_variants < kfolds):
                continue
            valid_pos_ind.append(pos_ind)
            np.random.seed(seed)
            neg_ind = np.random.choice(num_matched_variants, size=kfolds, replace=False)
            all_neg_variants.append(filtered_df.iloc[neg_ind,  :])
            processed_count += 1
        self.pos_variants_df = gnomad_pos_gwas_df.loc[valid_pos_ind, :]
        self.neg_variants_df = pd.concat(all_neg_variants, axis=0, ignore_index=True)
        print(self.neg_variants_df.shape)
        self.neg_variants_df.drop_duplicates(['chrom', 'pos'], inplace=True)
        print(self.neg_variants_df.shape)
        return self.neg_variants_df
    
    def get_pos_variants_df(self):
        """get positive variants dataframe"""

        if self.pos_variants_df is None:
            raise TypeError(f"Do negative loci matching first")
        return self.pos_variants_df

    def get_neg_variants_df(self):
        """get negative variants dataframe"""

        if self.neg_variants_df is None:
            raise TypeError(f"Do negative loci matching first")
        return self.neg_variants_df

    def variants_coor_to_tsv(self):
        out_coor_fn = os.path.join(self.out_coor_dir, f"{self.study_accession}_variants.tsv")
        coor_df = pd.concat([self.pos_variants_df, self.neg_variants_df], axis=0, ignore_index=True)
        sorted_coor_df = self._sort_genomic_coor_df(coor_df)
        sorted_coor_df = sorted_coor_df.loc[:, ['chrom', 'pos']]
        sorted_coor_df = self._add_two_side_win_nums(sorted_coor_df)
        sorted_coor_df.to_csv(out_coor_fn, index=False, header=False, sep='\t')
        return out_coor_fn

    def _generate_selected_risk_variants_df(self):
        """select positive SNPs for modeling based on study accession"""

        selected_risk_gwas_df = self.risk_gwas_df[self.risk_gwas_df['STUDY ACCESSION']==self.study_accession]
        selected_risk_gwas_df.rename(columns={'CHR_ID': 'Chromosome', 'CHR_POS': 'Start'}, inplace=True)
        selected_risk_gwas_df.loc[:, "End"] = selected_risk_gwas_df["Start"]
        selected_cols = ["Chromosome", "Start", "End", "SNP_ID_CURRENT", "P-VALUE", "PVALUE_MLOG", "CONTEXT"]
        selected_risk_gwas_df = selected_risk_gwas_df.loc[:, selected_cols]
        selected_risk_gwas_df.loc[:, 'Chromosome'] = "chr" + selected_risk_gwas_df['Chromosome'].astype(int).astype(str)
        selected_risk_gwas_df.loc[:, 'SNP_ID_CURRENT'] = 'rs' + selected_risk_gwas_df['SNP_ID_CURRENT'].astype(int).astype(str)
        selected_risk_gwas_df = selected_risk_gwas_df.loc[selected_risk_gwas_df['SNP_ID_CURRENT'].isin(self.gnomad_all_gwas_df['rsid']), :]
        return selected_risk_gwas_df
    
    def _sort_genomic_coor_df(self, df):
        df['chrom_int'] = df['chrom'].str.strip('chr').replace('X', '24', regex=False).astype(int)
        df = df.sort_values(by=['chrom_int', 'pos'], ascending=True)
        df.drop('chrom_int', axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def _add_two_side_win_nums(self, df):
        """
        generate search coor range for tabix matching
        Note: tabix is left-inclusive right-exclusive
        """
        df.loc[:, "search_start"] = df.pos - self.win_size*self.win_num
        df.loc[:, "search_end"] = df.pos + self.win_size*self.win_num + 1 
        # edge cases:
        # 1) search start point is negative
        df.loc[df.search_start<=0, 'search_start'] = 1
        # 2) search end point surpass the chromosome length
        if not self.chrom_length_fn:
            sys.exit("Error: Needs provide a chromosome length csv when initializing the instance")
        else:
            chrom_len_df = pd.read_csv(self.chrom_length_fn, names=["chrom", "length"])
        for chrom in df['chrom'].unique():
            chrom_size = chrom_len_df[chrom_len_df.chrom==chrom]['length'].values[0]
            df.loc[(df.chrom==chrom)&(df.search_end>(chrom_size+1)), 'search_end'] = chrom_size + 1
        df['prev_win_num'] = (df.loc[:, 'pos'] - df.loc[:, 'search_start'])//self.win_size
        df['post_win_num'] = (df.loc[:, 'search_end'] - df.loc[:, 'pos']-1)//self.win_size
        df['center_snp'] = df['chrom'].str.cat(df['pos'].astype(str), sep="_")
        df = df[['chrom', 'search_start', 'search_end', 'prev_win_num', 'post_win_num', 'center_snp']]
        return df
