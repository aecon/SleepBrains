import os
import sys
import nrrd
import mmap
import numba
import argparse
import numpy as np
import pandas as pd



@numba.jit(nopython=True, parallel=True, fastmath=True)
def colour(inputs, outputs, labels, colour):
    nx,ny,nz = inputs.shape  # checked: nrrd load data in (Y,X,Z) format
    for i in numba.prange(nx):
        for j in numba.prange(ny):
            for k in numba.prange(nz):
                label = inputs[i,j,k]
                if label > 0:
                    idx = label-1
                    outputs[i,j,k] = colour[idx]


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="csv, list with object measurements")
args = parser.parse_args()


file_csv = args.i
file_labels = find_file( os.path.dirname(file_csv) + os.sep + "labelled_" + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )
file_raw    = find_file( (os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("segmented_")[1]).split("-morpho")[0] + ".tif.nrrd"  )

assert(0)


print("Loading brain ...")
brain, _ = nrrd.read(file_labels)
brain = np.asarray(brain, dtype=np.uint32)

print("Loading csv ...")
data = pd.read_csv(file_csv)
# Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius
labels  = data["Label"].to_numpy()
volumes = data["VoxelCount"].to_numpy()
cx      = data["Centroid.X"].to_numpy()
cy      = data["Centroid.Y"].to_numpy()
cz      = data["Centroid.Z"].to_numpy()
spericity=data["Sphericity"].to_numpy()


print("Colouring brain ...")
assert(len(labels) == np.max(labels))
# - by volume
brain_coloured_volume = np.zeros(np.shape(brain), dtype=np.int32)
colour(brain, brain_coloured_volume, labels, volumes)
# - by sphericity
brain_coloured_sph = np.zeros(np.shape(brain), dtype=np.float32)
colour(brain, brain_coloured_sph, labels, spericity)


# Save coloured brain
print("Saving coloured brain ...")
nrrd.write('%s_colouredVolume.nrrd' % file_labels, brain_coloured_volume)
print("Saving coloured brain ...")
nrrd.write('%s_colouredSphericity.nrrd' % file_labels, brain_coloured_sph)

