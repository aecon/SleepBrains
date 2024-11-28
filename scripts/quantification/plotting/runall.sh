#!/bin/bash
set -eu


outdir="out"
mkdir -p $outdir


# Collect per-region counts
#./run_regions_collect.sh /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/region_counts_Brain*_centroids.txt > $outdir/data_regions_centroids.dat
#./run_regions_collect.sh /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/region_counts_Brain*_all.txt > $outdir/data_regions_allvoxels.dat


# Generate coronal with counts plots per sample
mkdir -p ${outdir}/density
folders=`ls -d /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*`
for d in ${folders[@]};
do
    echo $d
    brainid=`basename $d | awk -F  "_" '{print $1}'`

    f="${d}/aligned_points_on_grid_${brainid}_centroids.nrrd"
    python coronal_per_sample.py -i "$f" -o "${outdir}/density" -s "${brainid}_centroids" -n 0.05

    f="${d}/aligned_points_on_grid_${brainid}_all.nrrd"
    python coronal_per_sample.py -i "$f" -o "${outdir}/density" -s "${brainid}_allvoxels" -n 70
done

