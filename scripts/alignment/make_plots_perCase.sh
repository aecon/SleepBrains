#!/bin/bash
set -eu

parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09"

# FILES
brains=`find $parentdir/Brain*/align/elastix_affine_noBulb_try11 -name result.0.nrrd`

# OUTPUT DIRECTORY
outdir="out_elastix_affine_noBulb_try11"
mkdir -p $outdir

# RUN
for brain in ${brains}; do 
    #echo "Processing:" $brain

    d0=`dirname $brain`
    d1=`dirname $d0`
    d2=`dirname $d1`
    sampleID=`basename $d2`

    logfile=$d0/elastix.log
    atlas=`cat $logfile  | grep "\-f" | awk 'NR==2' | awk -F  '-f' '{print $2}' | awk '{ gsub (" ", "", $0); print}'`

    ls $brain
    ls $atlas
    ls $outdir
    echo $sampleID

    python plot_alignment.py -b $brain -a $atlas -o $outdir -s $sampleID
done
