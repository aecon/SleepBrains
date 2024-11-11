#!/bin/bash
set -eu


parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09"

brains=`find $parentdir/Brain* -name cropped_*_ch_0.tif.nrrd`
#
# specifically from Brain 9 - missing Cerebellum and Brain stem
#brains=`find $parentdir/Brain9_* -name cropped_*_ch_0.tif.nrrd`

for brain in ${brains}; do 
    echo "Processing:" $brain

    outdir=`dirname $brain`/align
    echo $outdir

    ./run_elastix_atlas2autof_SLEEP.sh "$outdir" "$brain"
done
