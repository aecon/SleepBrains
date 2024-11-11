# SleepBrains
Quantification of plaques and microglia cells in murine brains.



## TODO
### preprocessing
- [x] Preprocess: Conversion from tif to raw and crop.

### segmentation
- [x] Segment plaques.
- [x] Check plaques segmentation.
- [ ] Filter-out artifacts: Analyze Particles works on 2D. MorphoLibJ can compute per object measurements. Use them to filter out objects. Can do in ImageJ or python needed?
- [ ] Segment microglia.
- [ ] Check microglia segmentation.

### alignment
- [x] Align all brains (plaque channel).
- [ ] Align Brain 09 separately, due to missing Cerebellum and Brain stem: Removing these from the Atlas improved the alignment but it is not good yet.
- [x] Make coronal plots per brain.
- [x] Check alignment quality: All good except for Brain 10 (large hole - will be exluded, and Brain 9 - missing lower part)
- [x] Use transformix to align annotation atlas with regions.

### quantification
- [ ] Count plaques per region, export in txt.
- [ ] Make statistics plots.
- [ ] Voxel-wise pvalues: Compute average number of plaques per voxel. -> NEED TO BE ALIGNED ON THE SAME SPACE FOR THIS..
