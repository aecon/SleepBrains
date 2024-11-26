import os
import nrrd
import argparse
import skimage.io
import numpy as np


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, nargs='+', required=True, help="txt files, XYZ points")
    args = parser.parse_args()

    #file_atlas = '/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/selected_atlas_areas_pixel25um_noBulb.nrrd'
    file_atlas = "/Users/athena/Downloads/selected_atlas_areas_pixel25um_noBulb.nrrd"
    pixel_size = 25  # microns per pixel

    # Load atlas
    regions, _ = nrrd.read(file_atlas)
    regions = regions.astype(np.int64)
    nx,ny,nz = regions.shape

    for file_points in args.i:
        print("Processing:", file_points)
    
        # Load XYZ points
        points = np.loadtxt(file_points, skiprows=2)
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

