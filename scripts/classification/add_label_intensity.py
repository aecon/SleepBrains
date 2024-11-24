import os
import sys
import nrrd
import mmap
import numba
import argparse
import numpy as np
import pandas as pd


# ALSO HAS TO BE RUN WITH PARALLEL=FALSE!
@numba.jit(nopython=True, parallel=False, fastmath=True)
def get_intensity_stats(raw, labels, volumes, coordinates, intensity_mean, intensity_std):
    nx,ny,nz = raw.shape  # checked: nrrd loads data in (Y,X,Z) format
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
            print(g+2, i, volume, base, len(coordinates))
            assert((g+2) < len(coordinates))
            pi = int(coordinates[g + 0])
            pj = int(coordinates[g + 1])
            pk = int(coordinates[g + 2])
            assert((pi<nx) and (pj<ny) and (pk<nz))
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
parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
args = parser.parse_args()

# Find paths
for file_csv in args.i:
    print("\nProcessing:", file_csv)
    file_labels = find_file( os.path.dirname(file_csv) + os.sep + "labelled_" + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )
    file_raw    = find_file( (os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("segmented_")[1]).split("-morpho")[0] + ".tif.nrrd"  )

    # Load 3D data
    raw      = load_nrrd(file_raw, dtype=np.uint16)
    labels3F = load_nrrd(file_labels, dtype=np.float32)  # MLJ output is in float32
    labels3  = labels3F.astype(np.int64)

    # Load csv data
    df = pd.read_csv(file_csv)
    labels  = df["Label"].to_numpy()
    volumes = df["VoxelCount"].to_numpy()  # In Voxels

    # Checks
    assert(len(labels) == np.max(labels))
    assert(np.max(labels) == np.max(labels3))
    assert(volumes.dtype == np.int64)
    assert(labels.dtype == np.int64)
    assert(labels3.dtype == np.int64)

    # Compute object intensity stats (mean, std)
    #
    # --> Step 1: Get all coordinates per object
    print("Computing intensity stats ...")
    sumVolumes = np.sum(volumes)
    print("Sum of all object volumes:", sumVolumes)
    assert(sumVolumes.dtype == np.int64)
    coordinates = np.zeros((sumVolumes*3), dtype=np.int64)
    counts_cumsum  = np.cumsum(volumes) #.astype(np.int64)
    assert(counts_cumsum.dtype == np.int64)
    assert(0)
    print("- Getting coordinates")
    get_coordinates(labels3, labels, volumes, counts_cumsum, coordinates)
    #
    # --> Step 2: Compute intensity stats per object
    intensity_mean = np.zeros(len(labels))
    intensity_std  = np.zeros(len(labels))
    print("- Getting intensity stats")
    get_intensity_stats(raw, labels, volumes, coordinates, intensity_mean, intensity_std)

    # Add column to dataframe
    df['IntensityAvg'] = intensity_mean
    df['IntensityStd'] = intensity_std

    # Export to csv
    print("Exporting to csv ...")
    output_path = file_csv + "_withIntensity.csv"
    df.to_csv(output_path, index=False)

