library(data.table)
library(fst)
library(matrixStats)
library(dplyr)

args = commandArgs(trailingOnly=TRUE)
if (length(args)!=3) {
  stop("usage: Rscript 04_merge_processed_counts.R root_dir assay_type tech_rep_lst_dir", call.=FALSE)
} else {
  # default output file
  root.dir = args[1] 
  assay.type = args[2]
  tech.rep.lst.dir = args[3]
}

processed_dir = file.path(root.dir, "processed")
merged_dir = file.path(root.dir, "merged")

processed.csvs = list.files(processed_dir, pattern="*.csv", full.names=T)

print(sprintf("%i files to merge...", length(processed.csvs)))

datalist = list()
for (i in 1:length(processed.csvs)) {
  print(i)
  fn <- processed.csvs[i]
  curr.dt <- fread(fn) 
  datalist[[i]] <- curr.dt
}

print("Start merging data list...")
start_time = Sys.time()
merged.dt <- bind_cols(datalist)
end_time = Sys.time()
cat(sprintf("merging takes: %.3f\n", (end_time-start_time)))
rm(datalist)

#simulations
#meta.fn <- "/Users/yantinghuang/Study/DL_based_functional_annotation/ENCODE/filtered_metadata/filtered_Histone_Chipseq_metadata.csv"
#meta.dt <- fread(meta.fn)
#nums <- matrix(runif(100*(dim(meta.dt)[1])), ncol=dim(meta.dt)[1])
#counts.dt <- data.table(nums)
#colnames(counts.dt) <- meta.dt[["File accession"]]

# merge technical replicates
#tech.merge.fn <- "/Users/yantinghuang/Study/DL_based_functional_annotation/ENCODE/technique_rep_merge_accessions/Histone_Chipseq_tech_replicates.csv"

tech.merge.fn = file.path(tech.rep.lst.dir, sprintf("%s_tech_replicates.csv", assay.type))
if (file.exists(tech.merge.fn)) {
  print("start merging technical replicates...")
  tech.rep.dt <- fread(tech.merge.fn, header=T, sep=",")
  for (m in tech.rep.dt[["merge_list"]]) {
    print(m)
    cols.to.merge <- strsplit(m, ";")[[1]]
    new.col.name <- paste(cols.to.merge, collapse="_")
    merged.dt[,  (new.col.name):=rowMeans(as.matrix(.SD)), .SDcols=cols.to.merge]
    merged.dt[, (cols.to.merge):=NULL]
    print(dim(merged.dt))
  }
} else {
  print("no need to merge tech duplicates")
}
  
#write out the data to the disk
#merged.csv.fn <- file.path(merged_dir, sprintf("%s_merged_counts.csv", assay.type))
#fwrite(merged.dt, merged.csv.fn)
#print("writing csv completed...")

wins100.fn <- "/home/yanting/DL_based_functional_annotation/ENCODE/commons/wins100.txt"
wins100.dt <- fread(wins100.fn)

merged.dt <- bind_cols(list(wins100.dt, merged.dt))
merged.tsv.fn <- file.path(merged_dir, sprintf("%s_merged_counts.tsv", assay.type))
merged.tsv.gz.fn <- file.path(merged_dir, sprintf("%s_merged_counts.tsv.gz", assay.type))
fwrite(merged.dt, merged.tsv.fn, sep="\t")
bgzip.command <- paste("bgzip", "-f", "--threads 20", merged.tsv.fn, sep=" ")
tabix.command <- paste("tabix -s1 -b2 -e3 -f -p bed -S 1", merged.tsv.gz.fn, sep=" ")
print("start bgzip compressing...")
system(bgzip.command)
print("start making tabix index...")
system(tabix.command)
print("completed...")

print("start writing fst...")
merged.fst.fn <- file.path(merged_dir, sprintf("%s_merged_counts.fst", assay.type))
write.fst(merged.dt, merged.fst.fn, 100)
print("writing fst completed...")

