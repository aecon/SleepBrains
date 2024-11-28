#!/bin/bash
#
# ./run_regions_collect.sh /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/region_counts_Brain*_centroids.txt > data_regions_centroids.dat
# ./run_regions_collect.sh /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/region_counts_Brain*_all.txt > data_regions_allvoxels.dat

set -eu

# Sorted:
# 1 CB 819496
# 2 HB 452692
# 3 HPF 682678
# 4 HY 117093
# 5 Isocortex 2005659
# 6 Other 2928295
# 7 TH 51202

printf "%10s %20s %15s %15s %15s %15s %15s\n" "Sample" "HippocampalFormation" "Isocortex" "Thalamus" "Hypothalamus" "Midbrain" "Brain stem"
for f; do

    brainid=`basename $f | awk -F  "counts_" '{print $2}' | awk -F  "_" '{print $1}'`

    r1=`cat $f  | awk 'NR==1 {print $NF}'`
    r2=`cat $f  | awk 'NR==2 {print $NF}'`
    r3=`cat $f  | awk 'NR==3 {print $NF}'`
    r4=`cat $f  | awk 'NR==4 {print $NF}'`
    r5=`cat $f  | awk 'NR==5 {print $NF}'`
    r6=`cat $f  | awk 'NR==6 {print $NF}'`

    printf "%10s %20d %15d %15d %15d %15d %15d\n" $brainid $r1 $r2 $r3 $r4 $r5 $r6
done
