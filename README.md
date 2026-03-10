# SleepBrains
Quantification of plaques and microglia cells in murine brains.


## Installation
```
conda create -n SleepBrains -c conda-forge python=3.10
conda activate SleepBrains

pip install allensdk
pip install ipykernel
python -m ipykernel install --user --name=allensdk

pip install scikit-image numpy matplotlib pandas pynrrd numba scipy
```

AllenSDK: https://allensdk.readthedocs.io/en/latest/install.html


## Pipeline
**1. Preprocessing**  
```
cd scripts/pre-process 
Run:
* 1_convert.ijm
* 1-1_change_properties.ijm
* 2_crop.ijm
```
Ongoing: Combine all pre-processing steps in one:
```
scripts/pre-process/1_preprocess.ijm - WIP!!
```


**2. Segmentation**  
* 1. Use ilastik to get a probability map for plaques and microglia.  
```
cd ilastik/inference
./run_inference.sh    ## Edit paths to the trained .ilp file and .raw brains
```
* 2. Threshold probability map and run connected components (ImageJ).  
```
ilastik/macros/n5_to_csv.ijm  ## Edit paths to .n5 files (output from ilastik)
```
* 3. Filter-out false positives using probability map.
```
WIP!!
```


**3. Alignment**  
* 1. Generate pre-processes file to use for alignment.  
!! IMPORTANT: Pixel dimensions must be correct !!
```
scripts/alignment/preprocess_for_alignment.ijm
```
* 2. Alignment:  
Check paths to atlas (without bulb), atlas pixel size (25um), paths to affine and B-spline parameter files.
```
scripts/alignment//runall.sh
```
* 3. Plotting:
```
scripts/alignment/make_plots_perCase.sh
```

**4. Quantification**
* Run region-based analysis.



## TODO List
### preprocessing
- [x] Preprocess: Conversion from tif to raw and crop.

### segmentation
- [x] Segment plaques.
- [x] Check plaques segmentation.
- [x] Filter-out artifacts: Analyze Particles works on 2D. MorphoLibJ can compute per object measurements. Use them to filter out objects. Can do in ImageJ or python needed?
- [ ] Segment microglia.
- [ ] Check microglia segmentation.

### alignment
- [x] Align all brains (plaque channel).
- [ ] Align Brain 09 separately, due to missing Cerebellum and Brain stem: Removing these from the Atlas improved the alignment but it is not good yet.
- [x] Make coronal plots per brain.
- [x] Check alignment quality: All good except for Brain 10 (large hole - will be exluded, and Brain 9 - missing lower part)
- [x] Use transformix to align annotation atlas with regions.

### quantification
- [x] Count plaques per region, export in txt.
- [x] Code is too slow (was developed for smaller brains). Export list of plaque centers, do transformix on points list, then count inside regions.
- [x] Make statistics plots.
- [x] Voxel-wise pvalues: Compute average number of plaques per voxel. -> NEED TO BE ALIGNED ON THE SAME SPACE FOR THIS..

