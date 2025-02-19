import os
import sys
import nrrd
import numba
import argparse
import skimage.io
import numpy as np
import pandas as pd
import gc


# DESIGNED TO RUN WITH PARALLEL=FALSE.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def remove_non_plaques(labels3, is_plaque, coordinates):
#                       int64      0/1        float32
    nx,ny,nz = labels3.shape  # checked: nrrd loads data in (Y,X,Z) format

    # Loop over the image, once
    counter = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):  # C order (row major)
                l = labels3[i,j,k]
                if l>0:
                    idx = l-1
                    if is_plaque[idx] == 0:
                        # GOAL 1: Remove non-plaques from labels3 
                        labels3[i,j,k] = 0
                    else:
                        # GOAL 2: Collect physical coordinates of all plaque voxels 
                        coordinates[counter, 0] = float(i) * 3.26  # um per pixel
                        coordinates[counter, 1] = float(j) * 3.26
                        coordinates[counter, 2] = float(k) * 3.00
                        counter = counter + 1
    assert(counter == len(coordinates))


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
    return data.astype(dtype)


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
 
        self.eps = np.finfo(np.float32).eps  # machine precision
        self.intensity_ratio = self.intensity_std / (self.intensity_avg + self.eps) * 100.



def generate_list_of_points(X, Y, Z, output_file):
    # Generates a list of points according to the
    # input for elastix's transformix
    Np = len(X)
    with open(output_file, "w") as f:
        f.write("point\n")        # Line 1: "point" in physical coordinates
        f.write("%d\n" % Np)      # Line 2: number of points
        for i in range(Np):       
            f.write("%f %f %f\n" % (X[i], Y[i], Z[i]))


def generate_list_of_points_with_properties(X, Y, Z, VOL, PAVG, output_file):
    # Generates a list of points according to the
    # input for elastix's transformix
    Np = len(X)
    with open(output_file, "w") as f:
        f.write("X(um),Y(um),Z(um),NumberOfVoxels, AverageProbability\n")
        for i in range(Np):       
            f.write("%f %f %f %d %f\n" % (X[i], Y[i], Z[i], VOL[i], PAVG[i]))




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
    args = parser.parse_args()

    # Thresholds
    # THRES_s = 0    # sphericity threshold, should be greater than. Not used. Merged plaques have low sphericity and are wrongly excluded.
    THRES_vmax = 10000  # volume count threshold, should be less than
    THRES_vmin = 2   # volume count threshold, should be more or equal than
    THRES_i = 10     # intensity threholds, should be greater than


    for file_csv in args.i:
        print("\nProcessing:", file_csv)

        # Load ORIGINAL csv-file data
        D0 = CSVdata(file_csv)
        assert(len(D0.labels) == np.max(D0.labels))
        assert(D0.volumes.dtype == np.int64)
        assert(D0.labels.dtype == np.int64)

        # Keep only plaque objects
        idx = (D0.volumes<THRES_vmax) * (D0.volumes>=THRES_vmin) * (D0.intensity_ratio>=THRES_i)

        # EXPORT 1: List of plaque centroids - for transformation (alignment)
        basename = (os.path.basename(file_csv).split("_Probabi")[0]).split("original_")[1]
        output_file = '%s/coordinates_%s_centroids.txt' % (os.path.dirname(file_csv), basename)
        generate_list_of_points(D0.cx[idx], D0.cy[idx], D0.cz[idx], output_file)

        # EXPORT 2: List of plaque centroids AND properties: Volume and Average Probability
        output_file = '%s/coordinates_%s_centroids_with_measurements.csv' % (os.path.dirname(file_csv), basename)
        generate_list_of_points_with_properties(D0.cx[idx], D0.cy[idx], D0.cz[idx], D0.volumes[idx], D0.intensity_ratio[idx], output_file)


#        # Load 3D data
#        file_labels = find_file( os.path.dirname(file_csv) + os.sep + "labelled_" + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )
#        print("Loading 3D labels ...")
#        labels3 = load_nrrd(file_labels, dtype=np.int64)  # MLJ output is in float32
#        assert(np.max(D0.labels) == np.max(labels3))
#        assert(labels3.dtype == np.int64)
#
#        # Labels that are plaques
#        is_plaque = np.zeros(np.shape(D0.labels))
#        is_plaque[idx] = 1
#        print(np.sum(is_plaque), np.sum(idx), len(D0.labels))
#
#        # Get plaques pixel coordinates
#        NplaquePixels = np.sum(D0.volumes[idx])
#        print(NplaquePixels)
#        coordinates_plaques = np.zeros((NplaquePixels,3), dtype=np.float32)
#        remove_non_plaques(labels3, is_plaque, coordinates_plaques)
#
#
#        # EXPORT 2: csv with all plaque voxels
#        output_file = '%s/coordinates_plaques_allvoxels.txt' % os.path.dirname(file_csv)
#        generate_list_of_points(coordinates_plaques[:,0], coordinates_plaques[:,1], coordinates_plaques[:,2], output_file)
#
#
# Takes too long to export (>10 minutes)
#        # EXPORT 3: labels3 with true plaques
#        print("Saving labels3 with true plaques ...")
#        output_file = file_labels + "_plaques.tif"
#        skimage.io.imsave(output_file, labels3.T, plugin="tifffile", check_contrast=False)


        del D0
#        del is_plaque
#        del labels3
#        del coordinates_plaques

        gc.collect()


