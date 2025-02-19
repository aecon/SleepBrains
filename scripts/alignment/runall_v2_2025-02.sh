#!/bin/bash
set -eu

KIND="488"  # Options: "488" OR "647"

# Cannot change the paths from before because then we cannot use the already aligned brains
parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/"

brains=`find $parentdir/Brain* -name prealignment_cropped_original_Brain*_ch_0.tif.nrrd`

for brain in ${brains}; do 
    echo "Processing:" $brain

    outdir=`dirname $brain`/align
    echo $outdir

    ./run_elastix_data2atlas_PointsTranformix_2025-02.sh "$outdir" "$KIND" "$brain"
done
