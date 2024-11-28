import os
import sys
import glob
import nrrd
import numba
import skimage.io
import numpy as np

from generate_atlas_masks import brain_regions_include


# DESIGNED TO RUN WITH PARALLEL=FALSE.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def count_points_in_region(regions, indices, Nregions):
    nx,ny,nz = regions.shape
    Np = len(indices)
    counts_per_region = np.zeros(Nregions, dtype=np.int64)
    for pi in range(Np):
        i = indices[pi,0]
        j = indices[pi,1]
        k = indices[pi,2]
        if ((i<nx) and (j<ny) and (k<nz)):  # exclude points outside Atlas space
            region_id = regions[i,j,k]
            if region_id > 0:  # if not background
                counts_per_region[region_id-1] += 1
    return counts_per_region



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

    paths_allvoxels = sorted(glob.glob("/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/align/transformix_all/outputpoints.txt"))
    paths_centroids = sorted(glob.glob("/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/align/transformix_centroids/outputpoints.txt"))

    file_atlas = '/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/selected_atlas_areas_pixel25um_noBulb.nrrd'
    pixel_size = 25  # microns per pixel

    # Load atlas
    regions, _ = nrrd.read(file_atlas)
    regions = regions.astype(np.int64)
    Nregions = len(np.unique(regions))-1  # subtract 1 for background
    assert(len(brain_regions_include)==Nregions)

    for file_all, file_centroids in zip(paths_allvoxels, paths_centroids):
        print("Processing:")
        print(file_centroids)
        print(file_all)

        # Loop over two different kinds of points: allvoxels and centroids
        kinds = ["all", "centroids"]
        files = [file_all, file_centroids]
        for file_points, kind in zip(files, kinds):
            # Load transformed points
            ##points = np.loadtxt(file_points, skiprows=2)
            points = load_points(file_points)

            Npoints = len(points)
            indices = (points // pixel_size).astype(np.int64)

            # Get number of points per region
            counts_per_region = count_points_in_region(regions, indices, Nregions)

            # Export to file
            basedir = os.path.dirname(os.path.dirname(os.path.dirname(file_points)))
            brainid = os.path.basename(basedir).split("_")[0]
            output_file = basedir + os.sep + "region_counts_" + brainid + "_%s.txt" % kind
            print(output_file)
            with open(output_file, "w") as f:
                for i in range(Nregions):
                    f.write("%s %d\n" % (brain_regions_include[i], counts_per_region[i]))

            # Bin transformed points on atlas space
            nx,ny,nz = regions.shape
            grid = np.zeros(np.shape(regions), dtype=np.float32)
            for p in range(Npoints):
                ix = indices[p,0]
                iy = indices[p,1]
                iz = indices[p,2]

                if ((ix<nx) and (iy<ny) and (iz<nz)):
                    grid[ix,iy,iz] += 1

            nrrd.write("%s/aligned_points_on_grid_%s_%s.nrrd" % (basedir, brainid, kind), grid)

