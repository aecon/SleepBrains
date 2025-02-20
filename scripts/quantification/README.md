# Quantification

Collect region-wise statistics.

1. Generate atlas mask containing the regions to be considered
```
python generate_atlas_masks.py
```

* Copy the generated file: `selected_atlas_areas.nrrd` inside the folder:
```
scripts/alignment/selected_atlas_areas_pixel25um_noBulb_2025-02.nrrd
```
* Then open this file in ImageJ, and also open the file `selected_atlas_areas_pixel25um_noBulb.nrrd`.
* Crop the new file to be the same size as the `_noBulb` file.
* Edit the Pixel Properties to be 25 microns.
* Save the file.


2. Generate text files with counts (and volumes) per region, and map pixels to 3D atlas grid
* Edit the path to the selected atlas regions in the variable `file_atlas`.
* Edit the path to the transformed points files: `paths_centroids`.
* Then run:
```
python 2_regional_counts_volumes_2025-02.py
```

**OR**
Use the following to get counts, volumes, total probability, and region volume
```
python 3_perObject.py
```


3. Plotting
```
cd plotting
```

