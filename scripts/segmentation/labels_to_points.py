import numpy as np
import pandas as pd
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
args = parser.parse_args()


for filename in args.i:
    data = pd.read_csv(filename)

    # Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius

    labels  = data["Label"].to_numpy()
    volumes = data["VoxelCount"].to_numpy()
    cx      = data["Centroid.X"].to_numpy()
    cy      = data["Centroid.Y"].to_numpy()
    cz      = data["Centroid.Z"].to_numpy()
    spericity=data["Sphericity"].to_numpy()


    # Threshold on volume (>= 7 voxels)
