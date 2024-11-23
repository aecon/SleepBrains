import os
import sys
import nrrd
import mmap
import numba
import argparse
import numpy as np
import pandas as pd



@numba.jit(nopython=True, parallel=False, fastmath=True)
def get_intensity_stats(raw, labels, volumes, coordinates, intensity_mean, intensity_std):
    Nlabels = len(labels)
    Npixels = len(coordinates)/3

    # Loop over the objects
    for idx in range(1, Nlabels):  # ignore the first object
        base = counts_cumsum[idx-1] * 3
        volume = int(volumes[idx])
        intensities = np.zeros(volume)
        # Loop over the pixel of the particular object
        for i in range(volume):
            g = int(base + i*3)
            pi = int(coordinates[g + 0])
            pj = int(coordinates[g + 1])
            pk = int(coordinates[g + 2])
            intensities[i] = raw[pi,pj,pk]

        # At the end of the loop for this object, compute mean, std
        intensity_mean[idx] = np.nanmean(intensities)
        intensity_std[idx]  = np.nanstd(intensities)


# HAS TO BE PARALLEL=FALSE! PARALLEL VERSION WILL HAVE RACE CONDITION ON COUNTER
@numba.jit(nopython=True, parallel=False, fastmath=True)
def get_coordinates(labels3, labels, volumes, counts_cumsum, coordinates):
    nx,ny,nz = labels3.shape  # checked: nrrd loads data in (Y,X,Z) format
    counter = np.zeros(len(labels))

    # Loop over the image, once
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):  # C order (row major)
                label = labels3[i,j,k]
                if label > 1:  # ignore the first object
                    idx = int(label-1)
                    base = counts_cumsum[idx-1] * 3
                    g = int(base + counter[idx] * 3)
                    coordinates[g + 0] = i
                    coordinates[g + 1] = j
                    coordinates[g + 2] = k
                    counter[idx] = counter[idx] + 1
    for i in range(1,len(labels)):
        assert(counter[i] == volumes[i])


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path


def load_nrrd(path, dtype):
    print("Loading:", os.path.basename(path))
    data, _ = nrrd.read(path)
    data = np.asarray(data, dtype=dtype)
    return data




parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="csv, list with object measurements")
args = parser.parse_args()

# Find paths
file_csv = args.i
file_labels = find_file( os.path.dirname(file_csv) + os.sep + "labelled_" + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )
file_raw    = find_file( (os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("segmented_")[1]).split("-morpho")[0] + ".tif.nrrd"  )

# Load 3D data
raw     = load_nrrd(file_raw, dtype=np.uint16)
labels3 = load_nrrd(file_labels, dtype=np.float32)  # MLJ output is in float32

# Load csv data
data = pd.read_csv(file_csv)
labels      = data["Label"].to_numpy()
volumes     = data["VoxelCount"].to_numpy()  # In Voxels

# Compute object intensity stats (mean, std)
#
# --> Step 1: Get all coordinates per object
assert(len(labels) == np.max(labels))
sumVolumes = np.sum(volumes)
coordinates = np.zeros( (sumVolumes*3) )
counts_cumsum  = np.cumsum(volumes).astype(np.uint64)
get_coordinates(labels3, labels, volumes, counts_cumsum, coordinates)
#
# --> Step 2: Compute intensity stats per object
intensity_mean = np.zeros(len(labels))
intensity_std  = np.zeros(len(labels))
get_intensity_stats(raw, labels, volumes, coordinates, intensity_mean, intensity_std)



assert(0)

print("Colouring brain ...")
assert(len(labels) == np.max(labels))
# - by volume
brain_coloured_volume = np.zeros(np.shape(labels3), dtype=np.int32)
colour(labels3, brain_coloured_volume, labels, volumes)
# - by sphericity
brain_coloured_sph = np.zeros(np.shape(labels3), dtype=np.float32)
colour(labels3, brain_coloured_sph, labels, spericity)


