# Quantification


## Pipieline after Filter-based approach

Process:  

1. Computes per-object intensity stats. Exports intensity columns in new csv files.  
Usage:  
```
cd after_filters
pyton 1_add_label_intensity.py -i <PATHS TO CSV FILES>
```

2. Colours candidate plaques by different attributes: volume, sphericity, ratio of intensity std/mean.   
Usage: RUN FOR A SINGLE TEST BRAIN, NO NEED TO RUN FOR ALL BRAINS.  
```
cd after_filters
python 2_volume_colour.py -i PATH_TO_CSV_FILE_WITH_INTENSITY_STATS
```
Use the resuts to adjust thresholds for the attributes in step (3).




3. Filters-out non-plaques. Exports the following files:  
* A txt file with a list of all plaques pixel coordinates in um.
* A txt file with a list of per-plaque centroids in um.
* A 3D brain, where only true plaques are labeled.  
Usage: Adjust attribute thresholds based on step (2).  
```
cd after_filters
python 3_filter_objects.py -i <PATHS TO CSV FILES WITH INTENSITY STATS>
```


## Pipeline after Machine Learning approach (ilastik)

1. Run ImagejJ macro:
```
`/media/user/SSD1/Athena/SOURCE/SleepBrains/ilastik/macros/n5_to_csv_csv.ijm`
```
- Change the path to the folder containing the n5 files.   
- ilp file 488-v4 exports the channels and z-frames flipped. The macro swaps them.  
- ilp 647 exports the z-stack correctly. The macro should be edited to not flip the stack when converting to nrrd.
* Reads nrrd, and performs object classification using per-object probability and size/shape metrics.
* Exports the centroids and the volumes of each plaque in a csv file.

2. Filter-out false positives:  
Do steps 1,2,3 from above but use the scripts inside the folder `after_ML`.  


2b. Use `2b_statistics.py` to generate plots with statistics about the size, probability ratio and sphericity of the objects.
```
python 2b_statistics.py -i PATH_TO_CSV_FILE_WITH_INTENSITY_STATS
```

