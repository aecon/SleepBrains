#!/bin/bash
set -eu


parentdir="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09"

brains=`find $parentdir/Brain* -name prealignment_cropped_original_Brain*_ch_0.tif.nrrd`
#brains=`find $parentdir/Brain5* -name cropped_*_ch_0.tif.nrrd`
#brains=`find $parentdir/Brain5_* -name cropped_*_ch_0.tif.nrrd_forAlignment_Max-800_Gauss3D-2.nrrd`
#brains=`find $parentdir/Brain5_* -name cropped_*_ch_0.tif.nrrd_forAlignment_Max-800_Gauss3D-2_Bin2_Gaus3D-1.nrrd`
#
# specifically from Brain 9 - missing Cerebellum and Brain stem
#brains=`find $parentdir/Brain9_* -name cropped_*_ch_0.tif.nrrd`

for brain in ${brains}; do 
    echo "Processing:" $brain

    outdir=`dirname $brain`/align
    echo $outdir

    #./run_elastix_atlas2autof_SLEEP.sh "$outdir" "$brain"
    ./run_elastix_data2atlas_PointsTranformix.sh "$outdir" "$brain"
done
