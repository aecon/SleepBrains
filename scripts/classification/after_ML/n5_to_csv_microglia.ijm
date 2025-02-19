input_directory = getDirectory("Choose directory containing all the .n5 folders");

files = getFileList(input_directory);
Nfiles = files.length;
setBatchMode(true);
for (i=0; i<Nfiles; i++) {
	if (files[i].contains("cropped_original_Brain")) {
		print(files[i]);

		// Load .n5 file
		run("HDF5/N5/Zarr/OME-NGFF ... ", "url=n5://file:"+ input_directory + files[i] +"/?exported_data virtual");
		
		// Get basename
		title = files[i];
		basename = title.substring(22,lengthOf(title)-4);  // currently ends in .n5
		print(basename);
		
		// Change pixel properties
		getDimensions(width, height, channels, slices, frames);
		print(width, height, channels, slices, frames);

		// Change properties (due to subsequent alignment step)
		run("Properties...", "channels=2 slices="+toString(slices)+" frames=1 pixel_width=3.2600 pixel_height=3.2600 voxel_depth=3.0000");
		Stack.setXUnit("microns");
		Stack.setYUnit("microns");
		Stack.setZUnit("microns");
		title0 = getTitle();
		
        // Split channels
        selectImage(title0);
        run("Make Subset...", "channels=1 slices=1-" + toString(slices));
        rename("ch1");

        selectImage(title0);
        run("Make Subset...", "channels=2 slices=1-" + toString(slices));
        rename("ch2");

		selectImage(title0);
		close();
		
        // Add probabilities from the two channels (big and small microglia)
		imageCalculator("Add create 32-bit stack", "ch1","ch2");
		title_pmap = getTitle();
		
		selectImage("ch1");
		close();
		selectImage("ch2");
		close();
		
		selectWindow(title_pmap);

		// Threshold
		run("Duplicate...", "duplicate");
		setThreshold(0.2, 10);  // remove as few true plaques as possible, while keeping them separated..
		setOption("BlackBackground", true);
		run("Convert to Mask", "method=Default background=Default black");
		title_mask = getTitle();

		//run connected components labelling via MLJ, save labelled image
		run("Connected Components Labeling", "connectivity=26 type=float");
		rename("labelled_"+basename);
		titleLabelled = getTitle();
		
		//get information on labelled objects (sphericity, etc.), save in .csv
		run("Analyze Regions 3D", "voxel_count volume surface_area sphericity centroid max._inscribed surface_area_method=[Crofton (13 dirs.)] euler_connectivity=26");
		MLJ_suffix = "-morpho";
		MLJ_results = titleLabelled + MLJ_suffix;		
		
		// Output directory
		outdir = input_directory + "nrrd/";
		File.makeDirectory(outdir);
		
		// save csv
		selectWindow(MLJ_results);
		outpath = outdir + MLJ_results + ".csv";
		saveAs("Results", outpath);
		
		// original pmap
		selectWindow(title_pmap);
		outpath = outdir + basename + ".nrrd";
		print("Saving to:", outpath);
		run("Nrrd ... ", "nrrd="+outpath);

		// labeled image
		selectWindow(titleLabelled);
		outpath = outdir + "labelled_" + basename + ".nrrd";
		print("Saving to:", outpath);
		run("Nrrd ... ", "nrrd="+outpath);
		
		//cleanup windows
		close("*");
		selectWindow(MLJ_results + ".csv");
		run("Close");
	}
}
