# Quantification

Collect region-wise statistics.

1. Generate atlas mask containing the regions to be considered
```
python generate_atlas_masks.py
```

2. Generate text files with counts (and volumes) per region
```
python 2_regional_counts_volumes.py -i <PATHS TO align/transformix_centroids/outputpoints.txt files> -o "centroid"
python 2_regional_counts_volumes.py -i <PATHS TO align/transformix_allvoxels/outputpoints.txt files> -o "allvoxels"
```
