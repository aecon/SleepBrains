import os
import sys
import nrrd
import mmap
import numba
import argparse
import numpy as np
import pandas as pd



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
    args = parser.parse_args()

    # Find paths
    for file_csv in args.i:
        print("\nProcessing:", file_csv)

        # Load csv data
        # Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius,IntensityAvg,IntensityStd

        df = pd.read_csv(file_csv)
        labels  = df["Label"].to_numpy()
        volumes = df["VoxelCount"].to_numpy()  # In Voxels


