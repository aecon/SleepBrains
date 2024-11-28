import os
import sys
import nrrd
import argparse
import skimage.io
import numpy as np


def load_points(file_points):
    database = np.genfromtxt(file_points, dtype='str', delimiter=";")
    Np = len(database)
    points = np.zeros((Np,3), dtype=np.float32)
    for i in range(Np):
        s = database[i,4].split("[")[1].split("]")[0]
        p = np.fromstring(s, dtype=float, sep=" ")
        assert(len(p)==3)
        points[i,0] = p[0]
        points[i,1] = p[1]
        points[i,2] = p[2]
    return points


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, nargs='+', required=True, help="txt, transformed points-file from transformix")
    parser.add_argument('-t', type=str, required=True, help="short or long")
    args = parser.parse_args()

    file_atlas = '/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/selected_atlas_areas_pixel25um_noBulb.nrrd'
    #file_atlas = "/Users/athena/Downloads/selected_atlas_areas_pixel25um_noBulb.nrrd"
    pixel_size = 25  # microns per pixel

    # Load atlas
    regions, _ = nrrd.read(file_atlas)
    regions = regions.astype(np.int64)
    nx,ny,nz = regions.shape

    for file_points in args.i:
        print("Processing:", file_points)
    
        # Load XYZ points
        if args.t == "long":
            points = load_points(file_points)
        elif args.t == "short":
            points = np.loadtxt(file_points, skiprows=2)
        else:
            print("Loading type not supported.")
            sys.exit()

        Npoints = len(points)
        indices = (points // pixel_size).astype(np.int64)

        grid = np.zeros(np.shape(regions), dtype=np.float32)

        for p in range(Npoints):
            ix = indices[p,0]
            iy = indices[p,1]
            iz = indices[p,2]

            if ((ix<nx) and (iy<ny) and (iz<nz)):
                grid[ix,iy,iz] += 1

        nrrd.write("grid_with_points.nrrd", grid)

