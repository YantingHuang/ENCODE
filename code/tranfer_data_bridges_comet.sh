#rsync option:
#-r: recurse into directories
#-l: copy symlinks as symlinks
#-t: preserve modification times
#-p: preserve permissions
#-D: preserve device files (super-user only)
#-v: increase verbosity
#-P: keep partially transferred files
#--delete: Deletes files in the destination directory if they don't exist in the source directory.
#--delete-before: Delete files in the destination directory before copying file-with-same-name from source directory

# in Comet
# transfer from Comet to Bridges
cometDir="/oasis/scratch/comet/yanting/temp_project/encode_data_processing"
bridgesDir="/pylon5/eg4s89p/yanting"
rsync -rltpDvP -e 'ssh -l yanting' ${cometDir} data.bridges.psc.edu:${bridgesDir}


# in Bridges
# transfer from Bridges to Comet
bridgesDir="/pylon5/eg4s89p/yanting/encode_data_processing/TF_ChIP_seq/merged"
cometDir="/oasis/scratch/comet/yanting/temp_project/encode_data_processing/TF_ChIP_seq"
rsync -rltpDvP -e 'ssh -l yanting' ${bridgesDir} comet.sdsc.xsede.org:${cometDir}
