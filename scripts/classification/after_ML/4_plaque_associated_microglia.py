import os
import sys
import nrrd
import mmap
import numba
import skimage.io
import argparse
import numpy as np
import pandas as pd


THRES_vmax = 10000  # volume count threshold, should be less than
THRES_vmin = 2   # volume count threshold, should be more or equal than
THRES_i = 10     # intensity threholds, should be greater than


class CSVdata():
    def __init__(self, file_csv:str):

        print("Loading csv file into pandas dataframe")
        self.df = pd.read_csv(file_csv)

        # - Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius,IntensityAvg,IntensityStd

        self.labels         = self.df["Label"].to_numpy()
        self.volumes        = self.df["VoxelCount"].to_numpy()  # number of voxels corresponding to object
        self.cx             = self.df["Centroid.X"].to_numpy()  # x-coordinate of object's centroid
        self.cy             = self.df["Centroid.Y"].to_numpy()
        self.cz             = self.df["Centroid.Z"].to_numpy()

        self.sphericity     = self.df["Sphericity"].to_numpy()
        self.intensity_avg  = self.df["IntensityAvg"].to_numpy()
        self.intensity_std  = self.df["IntensityStd"].to_numpy()
        self.intensity_sum  = self.df["IntensitySum"].to_numpy()
 
        self.eps = np.finfo(np.float32).eps  # machine precision
        self.intensity_ratio = self.intensity_std / (self.intensity_avg + self.eps) * 100.





# Written for parallel=FALSE
@numba.jit(nopython=True, parallel=False, fastmath=False)
def count_microglia_voxels_inside_plaques(plaques, microglia, microglia_counts):
    nx,ny,nz = plaques.shape
    for i in numba.prange(nx):
        for j in numba.prange(ny):
            for k in numba.prange(nz):
                plabel = plaques[i,j,k]
                mlabel = microglia[i,j,k]
                if (plabel>0 and mlabel>0):
                    l = plabel-1
                    microglia_counts[l] += 1


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="labeled plaque nrrd")
args = parser.parse_args()


for file_plaques in args.i:
    
    brainID = os.path.basename(file_plaques).split("Brain")[1].split("_")[0]
    print(file_plaques)
    print(brainID)
    if brainID == "09":
        continue

    file_microglia = find_file('/media/neptun/LocalDisk16TB/Athena/PROJECT_SLEEP_BRAINS_2025-02/to_ilastik/647/predictions_647_model2_Feb17/nrrd/labelled_cropped_original_Brain%s_647_Probabilities.nrrd' % brainID)
    file_csv = find_file( '/media/neptun/LocalDisk16TB/Athena/PROJECT_SLEEP_BRAINS_2025-02/to_ilastik/488/predictions_488_2025-02-12_AllBrains_Zcyx/nrrd/labelled_cropped_original_Brain%s_488_Probabilities-morpho.csv_withIntensity.csv'% brainID)

    print("Loading plaques")
    plaques, _ = nrrd.read(file_plaques)
    plaques = np.asarray(plaques, dtype=np.uint32)

    print("Loading microglia")
    microglia, _ = nrrd.read(file_microglia)
    microglia = np.asarray(microglia, dtype=np.uint32)

    print("Loading CSV data")
    D0 = CSVdata(file_csv)
    assert(len(D0.labels) == np.max(D0.labels))
    assert(D0.volumes.dtype == np.int64)
    assert(D0.labels.dtype == np.int64)

    print("Counting microglia voxels inside plaques")
    Nplaques = np.max(plaques)
    assert(Nplaques == np.max(D0.labels))
    microglia_counts = np.zeros(Nplaques, dtype=np.uint32)
    count_microglia_voxels_inside_plaques(plaques, microglia, microglia_counts)

    # Keep only microglia associated with true plaques
    idx = (D0.volumes<THRES_vmax) * (D0.volumes>=THRES_vmin) * (D0.intensity_ratio>=THRES_i)
    actual_plaque_microglia_counts = microglia_counts[idx]
    actual_plaque_counts = D0.volumes[idx]
    actual_plaque_labels = D0.labels[idx]

    # Save file
    output_file = os.path.dirname(file_microglia) + os.sep + "counts_plaque_associated_microglia_Brain%s.dat" % brainID
    with open(output_file, "w") as f:
     f.write("PlaqueLabel NumberOfMicrogliaVoxels NumberOfPlaqueVoxels\n")
     for i in range(len(actual_plaque_microglia_counts)):
         f.write("%d %d %d\n" % (actual_plaque_labels[i], actual_plaque_microglia_counts[i], actual_plaque_counts[i]))

    del plaques
    del microglia
    del microglia_counts
    del D0
    del actual_plaque_microglia_counts
    del idx

