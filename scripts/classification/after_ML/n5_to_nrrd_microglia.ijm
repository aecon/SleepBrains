//input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/test_ilastik/";
//input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/ilastik/ilastik_probabilities/predictions_488_allBrains_ilp-v4/";

input_directory = getDirectory("Choose directory");

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
		titleP = getTitle();
		
		selectImage("ch1");
		close();
		selectImage("ch2");
		close();

		// Save as nrrd
		selectImage(titleP);
		outdir = input_directory + "nrrd/";
		File.makeDirectory(outdir);
		outpath = outdir + basename + ".nrrd";
		print("Saving to:", outpath);
		run("Nrrd ... ", "nrrd="+outpath);

		close("*");
	}
}
