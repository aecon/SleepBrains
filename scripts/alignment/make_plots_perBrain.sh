#!/bin/bash
set -eu

parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09"

# FILES
#brains=`find $parentdir/Brain*/align/elastix_bspline -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_affine -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid50-300_6000samples_NoBulb -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid50-300_6000samples -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05 -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05 -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_affine_noBulb_try05 -name result.0.nrrd`
brains=`find $parentdir/Brain5_*/align/elastix_* -name result.0.nrrd`

# OUTPUT DIRECTORY
#outdir="out_withBulb_try05"
#outdir="out_noBulb_affine_try05"

# ATLAS
#atlas="atlas/ABA_25um_reference_hemisphere.nrrd"

# RUN
for brain in ${brains}; do 
    #echo "Processing:" $brain

#    d0=`dirname $brain`
#    d1=`dirname $d0`
#    d2=`dirname $d1`
#    sampleID=`basename $d2`

    d0=`dirname $brain`
    sampleID=`basename $d0`
    outdir=`dirname $d0`/plots
    logfile=$d0/elastix.log

    atlas=`cat $logfile  | grep "\-f" | awk 'NR==2' | awk -F  '-f' '{print $2}' | awk '{ gsub (" ", "", $0); print}'`

    mkdir -p $outdir

    ls $brain
    ls $atlas
    ls $outdir
    echo $sampleID

    python plot_alignment.py -b $brain -a $atlas -o $outdir -s $sampleID
done
