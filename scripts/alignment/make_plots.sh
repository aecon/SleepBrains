#!/bin/bash
set -eu

parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09"

#brains=`find $parentdir/Brain*/align/elastix_bspline -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_affine -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid50-300_6000samples_NoBulb -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid50-300_6000samples -name result.0.nrrd`
#brains=`find $parentdir/Brain*/align/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05 -name result.0.nrrd`
brains=`find $parentdir/Brain*/align/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05 -name result.0.nrrd`

outdir="out_withBulb_try05"

atlas="atlas/ABA_25um_reference_hemisphere.nrrd"

mkdir -p $outdir

for brain in ${brains}; do 
    #echo "Processing:" $brain

    d0=`dirname $brain`
    d1=`dirname $d0`
    d2=`dirname $d1`
    sampleID=`basename $d2`

    echo $brain
    echo $atlas
    echo $sampleID

    python plot_alignment.py -b $brain -a $atlas -o $outdir -s $sampleID
done
