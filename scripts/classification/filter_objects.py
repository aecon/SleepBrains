import os
import sys
import argparse
import numpy as np
import pandas as pd


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
    args = parser.parse_args()

    # Find paths
    for file_csv in args.i:
        print("\nProcessing:", file_csv)

        # Load csv data
        # - Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius,IntensityAvg,IntensityStd
        print("Loading csv ...")
        data = pd.read_csv(file_csv)
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

        # Checks
        assert(len(labels) == np.max(labels))
        assert(volumes.dtype == np.int64)
        assert(labels.dtype == np.int64)

        # Filter-out non-plaque objects
        ts = 0.2    # >
        tv = 40000  # <
        ti = 15     # >
        idx = (spericity>ts) * (volumes<tv) * (IntensityRatio>ti)

        lbl_plaque = labels[idx]
        v_plaque = volumes[idx]
        cx_plaque = cx[idx]
        cy_plaque = cy[idx]
        cz_plaque = cz[idx]

        # Generate new plaques dataframe
        df_plaque = pd.DataFrame(columns=['Label', 'VoxelCount', 'Centroid.X', 'Centroid.Y', 'Centroid.Z'])
        df_plaque['Label'] = lbl_plaque
        df_plaque['VoxelCount'] = v_plaque
        df_plaque['Centroid.X'] = cx_plaque
        df_plaque['Centroid.Y'] = cy_plaque
        df_plaque['Centroid.Z'] = cz_plaque

        # Export to csv
        print("Exporting to csv ...")
        output_path = file_csv + "_PLAQUES.csv"
        df_plaque.to_csv(output_path, index=False)

