import os
import sys
import nrrd
import numba
import argparse
import numpy as np
import pandas as pd


@numba.jit(nopython=True, parallel=False, fastmath=True)
def test(brain):
    nx,ny,nz = brain.shape  # checked: nrrd load data in (Y,X,Z) format
    for i in numba.prange(nx):
        for j in numba.prange(ny):
            for k in numba.prange(nz):
                brain[i,j,k] = 10 + brain[i,j,k]


@numba.jit(nopython=True, parallel=False, fastmath=True)
def colour(inputs, outputs, labels, colour):
    nx,ny,nz = inputs.shape  # checked: nrrd load data in (Y,X,Z) format
    for i in numba.prange(nx):
        for j in numba.prange(ny):
            for k in numba.prange(nz):
                label = inputs[i,j,k]
                idx = np.where(labels == label)[0][0]
                outputs[i,j,k] = colour[idx]


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="csv, list with object measurements")
args = parser.parse_args()


file_labels = args.i
file_brain = os.path.dirname(file_labels) + os.sep + "labelled_" + os.path.basename(file_labels).split("-morpho")[0] + ".tif-lbl.nrrd"
print("Colouring brain:", file_brain)
if os.path.exists(file_brain):
    print("Found labeled brain!")
else:
    print("File not found... Exiting.")
    sys.exit()

print("Loading brain ...")
brain, _ = nrrd.read(file_brain)
brain = np.asarray(brain, dtype=np.uint32)

print("Loading csv ...")
data = pd.read_csv(file_labels)
# Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius
labels  = data["Label"].to_numpy()
volumes = data["VoxelCount"].to_numpy()
cx      = data["Centroid.X"].to_numpy()
cy      = data["Centroid.Y"].to_numpy()
cz      = data["Centroid.Z"].to_numpy()
spericity=data["Sphericity"].to_numpy()


print("Colouring brain ...")

# Colour by pixel volume
maxLabel = np.max(labels)
brain_coloured_volume = np.zeros(np.shape(brain), dtype=int)
test(brain)
colour(brain, brain_coloured_volume, labels, volumes)


# Save coloured brain
#print("Saving coloured brain ...")
#TODO
