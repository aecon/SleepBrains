import os
import sys
import nrrd
import mmap
import numba
import skimage.io
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
parser.add_argument('-i', type=str, required=True, help="csv, list with object measurements, with intensity stats")
parser.add_argument('-t', type=str, required=True, choices=['volume', 'sphericity', 'IstdIavg'], help="quantity to colour by")
args = parser.parse_args()


file_csv = args.i
file_labels = find_file( os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )

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
IntensityAvg=data["IntensityAvg"].to_numpy()
IntensityStd=data["IntensityStd"].to_numpy()

eps = np.finfo(np.float32).eps
IntensityRatio = IntensityStd / (IntensityAvg + eps) * 100.

assert(len(labels) == np.max(labels))

print("Colouring brain ...")
if args.t == 'volume':
    brain_coloured = np.zeros(np.shape(brain), dtype=np.int32)
    colour(brain, brain_coloured, labels, volumes)
elif args.t == 'sphericity':
    brain_coloured = np.zeros(np.shape(brain), dtype=np.float32)
    colour(brain, brain_coloured, labels, spericity)
elif args.t == 'IstdIavg':
    brain_coloured = np.zeros(np.shape(brain), dtype=np.float32)
    colour(brain, brain_coloured, labels, IntensityRatio)


# Save coloured brain   (Saving in tif is faster than in nrrd !)
print("Saving coloured brain ...")
skimage.io.imsave('%s_Coloured-%s.tif' % (file_labels, args.t), brain_coloured.T, plugin="tifffile", check_contrast=False)


del brain
del brain_coloured
del data, labels, volumes, cx, cy, cz, spericity, IntensityAvg, IntensityStd, IntensityRatio

