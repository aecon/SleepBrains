"""
run as:
python generate_region_stats.py -i /media/neptun/LocalDisk16TB/Athena/PROJECT_Elkhan/DATA/YOUNG_COHORT/brain*/brain*_em520_mask_crop.tif -a /media/neptun/LocalDisk16TB/Athena/PROJECT_Elkhan/DATA/YOUNG_COHORT/brain*/transformix/result.nrrd
"""

import os
import nrrd
import argparse
import skimage.io
import numpy as np

from generate_atlas_masks import brain_regions_include


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='+', required=True, help="segmented object labels, nrrd")
parser.add_argument('-a', type=str, nargs='+', required=True, help="aligned region labels, nrrd")
parser.add_argument('-oc', type=str, required=True, help="output txt file, counts")
parser.add_argument('-ov', type=str, required=True, help="output txt file, volumes")
args = parser.parse_args()
px = 13.04  # microns per pixel in x,y  # TODO: Correct!!
pz = 12.00  # microns per pixel in z


flist_label = sorted(args.i)
flist_atlas = sorted(args.a)

all_counts = []
all_volums = []

for f_regions, f_labels in zip(flist_atlas, flist_label):
    print("Processing:", f_regions, f_labels)

    # load files
    labels, _  = nrrd.read(f_labels)
    print("Read labels.")
    regions, _ = nrrd.read(f_regions)
    print("Read regions.")
    if np.shape(labels)!=np.shape(regions):
        continue

    Region_IDs = np.unique(regions)
    cell_counts = np.zeros(len(Region_IDs)-1)
    cell_volums = np.zeros(len(Region_IDs)-1)

    for i, rid in enumerate(Region_IDs):
        if rid > 0:
            print("Region:", rid)
            # Keep only cells inside region `rid`
            labels_in_region = np.zeros(np.shape(regions))
            idx = regions==rid
            labels_in_region[idx] = labels[idx]

            # compute volume of cells inside region
            volume = np.sum(labels_in_region>0) * px*px*pz

            # compute number of cells inside region
            counts = len(np.unique(labels_in_region))-1  # subtract 1 for background label

            # store in sample arrays
            cell_counts[i-1] = counts
            cell_volums[i-1] = volume
            print("counts:", counts, "volume:", volume)

    all_counts.append(cell_counts)
    all_volums.append(cell_volums)


# Store all counts/volums to file
with open(args.oc, 'w') as f:
    f.write("%10s " % "Sample")
    for br in brain_regions_include:
        f.write("%25s " % br)
    f.write("\n")
    for filename, sample in zip(flist_label, all_counts):
        f.write("%10s " % os.path.basename(os.path.dirname(filename)))
        for s in sample:
            f.write("%25g " % s)
        f.write("\n")

with open(args.ov, 'w') as f:
    f.write("%10s " % "Sample")
    for br in brain_regions_include:
        f.write("%25s " % br)
    f.write("\n")
    for filename, sample in zip(flist_label, all_volums):
        f.write("%10s " % os.path.basename(os.path.dirname(filename)))
        for s in sample:
            f.write("%25g " % s)
        f.write("\n")



