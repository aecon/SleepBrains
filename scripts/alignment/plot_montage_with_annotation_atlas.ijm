input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";
aligned_directory="align/elastix_bspline_10k_125umGrid1_SmoothAll2_noBulb_BsplineInterpolator_try20/"
file_atlas="/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/ABA_25um_annotation_hemisphere_noBulb.nrrd"
suffix="montage_aligned_annotation_atlas";

directories = getFileList(input_directory);
Ndir = directories.length;

// Loop over brain directories
setBatchMode(true);
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	if ( startsWith(directories[i],"Brain") ){

		// Find aligned brain
		file_aligned = input_directory + directories[i] + aligned_directory + "result.0.nrrd";
		if (File.exists(file_aligned)){
			print("  ", "File exists:", file_aligned);
		}
		else {
			print("File does NOT exist:", file_aligned);
			exit;
		}

		// aligned brain
		open(file_aligned);
		run("32-bit");
		run("Reslice [/]...", "output=25.000 start=Top rotate avoid");
		run("Slice Keeper", "first=35 last=456 increment=1");
		titleData = getTitle();

		// atlas
		open(file_atlas);
		run("Reslice [/]...", "output=25.000 start=Top rotate");  // with interpolation
		run("Find Edges", "stack");
		run("Slice Keeper", "first=35 last=456 increment=1");
		titleAtlas = getTitle();

		// merge
		run("Merge Channels...", "c4=["+titleData+"] c6=["+titleAtlas+"] create ignore");

		// montage
		run("Make Montage...", "columns=10 rows=1 scale=1 increment=40");

		// adjust colour
		Stack.setChannel(1);
		resetMinAndMax();
		run("Enhance Contrast", "saturated=0.35");

		Stack.setChannel(2);
		setMinAndMax(700, 2000);

        // save montage
        //-tif
        output_path = input_directory + directories[i] + suffix + ".tif";
        print("  ", "Saving to:", output_path);
        saveAs("Tiff", output_path);
		//-png
        output_path = input_directory + directories[i] + suffix + ".png";
        print("  ", "Saving to:", output_path);
        saveAs("PNG", output_path);

        // close all files
        run("Close All");
	}
}

print("DONE.");
exit;

