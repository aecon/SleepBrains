# ImageJ macros


## `convert_to_raw.ijm` 
- Run before ilastik.  
- Use to convert .nrrd files to .raw files, that have the appropriate name convention to be read by ilastik in headless and distributed model.


## `convert_n5_to_nrrd_with_PixelProperties.ijm`
- Run asfter ilastik.  
- Use to convert ilastik output (.n5) to .nrrd.  
- NOTE: DO NOT USE! n5 is compressed (3GB) whereas nrrd is not (30GB). n5 works well with ImageJ macro language.
