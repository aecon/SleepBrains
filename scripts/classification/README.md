# Quantification

Process:  

1. Computes per-object intensity stats. Exports intensity columns in new csv files.  
Usage:  
```
pyton 1_add_label_intensity.py -i <PATHS TO CSV FILES>
```

2. Colours candidate plaques by different attributes: volume, sphericity, ratio of intensity std/mean.   
Usage: RUN FOR A SINGLE TEST BRAIN, NO NEED TO RUN FOR ALL BRAINS.  
```
python 2_volume_colour.py -i PATH_TO_CSV_FILE_WITH_INTENSITY_STATS
```
Use the resuts to adjust thresholds for the attributes in step (3).


3. Filters-out non-plaques. Exports the following files:  
* A txt file with a list of all plaques pixel coordinates in um.
* A txt file with a list of per-plaque centroids in um.
* A 3D brain, where only true plaques are labeled.  
Usage: Adjust attribute thresholds based on step (2).  
```
python 3_filter_objects.py -i <PATHS TO CSV FILES WITH INTENSITY STATS>
```

