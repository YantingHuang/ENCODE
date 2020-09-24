 library(GenomicRanges)
#library(GenomicFeatures)
library(GenomicAlignments)
library(data.table)

read.bam <- function(bam.file, valid.chrNames, remove_dup=1){
  print("Start reading bam into memory...")
  bamParam = ScanBamParam(what=c("rname", "strand", "pos", "qwidth"))
  bam = readGAlignments(bam.file, param=bamParam)
  print("finished...")
  print("raw total #reads:")
  print(length(bam))
  ### filter according to seq names
  print("only preserving bam in valid chromosomes, #reads:")
  bam.chr.selected <- bam[seqnames(bam) %in% valid.chrNames]
  print(length(bam.chr.selected))
  if (length(bam.chr.selected) == 0) {
    print("uncommon results; needs check with chromosomes")
  }
  rm(bam)
  ix.gene.pos  = which(strand(bam.chr.selected)=="+")
  ix.gene.minus= which(strand(bam.chr.selected)=="-")
  starts = start(bam.chr.selected)
  starts[ix.gene.minus] = end(bam.chr.selected)[ix.gene.minus]
  bam.granges = GRanges(seqnames=Rle(seqnames(bam.chr.selected)),
                        ranges=IRanges(start=starts, width=1))
  if (remove_dup) {
    ### filter duplicated reads if needed
    print("perform duplicates reads trimming...")
    bam.granges = unique(bam.granges)
  }
  print("total #read:")
  print(length(bam.granges))
  return(bam.granges)
}

### main program starts from here
args = commandArgs(trailingOnly=TRUE)
if (length(args)!=3) {
  stop("usage: Rscript single_bam_file_processor.R bam_file win100_file output.dir", call.=FALSE)
} else {
  # default output file
  bam.file = args[1]
  win100_file = args[2] #"/home/yanting/DL_based_functional_annotation/ENCODE/commons/wins100.txt"
  output.dir = args[3]
}
# find the experiment name from the name of the bam
experiment.name <- strsplit(bam.file, split="\\.")[[1]][1]
experiment.name <- strsplit(experiment.name, split="/")[[1]]
experiment.name <- experiment.name[length(experiment.name)]
#work.dir should contain bam and wins100.txt
#setwd(work.dir)
#load("wins200.rda") 
wins = fread(win100_file)
print(dim(wins))
wins.gr = makeGRangesFromDataFrame(wins)
seqlevelsStyle(wins.gr) <- "UCSC" #naming style: chr1, chr2, ...
print(wins.gr)
valid.chrNames <- unique(seqnames(wins.gr))
# read bam
start_time = Sys.time()
bam.granges = read.bam(bam.file, valid.chrNames, remove_dup=1)
print(bam.granges)
end_time = Sys.time()
cat(sprintf("loading bam into memory and preprocessing takes: %.3f\n", (end_time-start_time)))

# find overlaps
print("Start counting read counts...")
start_time = Sys.time()
hits = findOverlaps(bam.granges, wins.gr, type='within')
win.counts = countSubjectHits(hits)
end_time = Sys.time()
print(head(win.counts))
print(sum(win.counts))
print("finished...")
cat(sprintf("find overlaps takes: %.3f\n", (end_time-start_time)))


#output the result into csv
start_time = Sys.time()
output.fn <- file.path(output.dir, paste0(experiment.name, ".csv"))

win.counts <- data.table(win.counts)
setnames(win.counts, experiment.name)
fwrite(win.counts, file=output.fn, sep=",", quote=FALSE)
end_time = Sys.time()
cat(sprintf("write the data into the disk takes: %.3f\n", (end_time-start_time)))
# delete bam when completed
file.remove(bam.file)
print("the bam file deleted...")


