//input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/test_ilastik/";
//input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/ilastik/ilastik_probabilities/predictions_488_allBrains_ilp-v4/";

input_directory = getDirectory("Choose directory");

files = getFileList(input_directory);
Nfiles = files.length;
for (i=0; i<Nfiles; i++) {
	if (files[i].contains("cropped_original_Brain")) {
		print(files[i]);

		// Load .n5 file
		run("HDF5/N5/Zarr/OME-NGFF ... ", "url=n5://file:"+ input_directory + files[i] +"/?exported_data virtual");

		// Get basename
		title = files[i];
		basename = title.substring(22,lengthOf(title)-4);  // currently ends in .n5
		print(basename);
		
		// Change pixel properties and swap channels and slices
		getDimensions(width, height, channels, slices, frames);
		print(width, height, channels, slices, frames);
		Z = channels;
		
		// Change properties (due to subsequent alignment step)
		run("Properties...", "channels=1 slices="+toString(Z)+" frames=1 pixel_width=3.2600 pixel_height=3.2600 voxel_depth=3.0000");
		Stack.setXUnit("microns");
		Stack.setYUnit("microns");
		Stack.setZUnit("microns");

		// Save as nrrd
		outdir = input_directory + "nrrd/";
		File.makeDirectory(outdir);
		outpath = outdir + basename + ".nrrd";
		print("Saving to:", outpath);
		run("Nrrd ... ", "nrrd="+outpath);

		close("*");
	}
}
