/*ImageJ macro building upon 4_segment_MGs by labelling objects and providing information about oject characteristics via MorphoLibJ
 * requires setting Plugins > Bio-Formats > Bio-Formats Plugins Configuration > Formats > Fei TIFF: enabled and windowless checked //TODO: add all other Tiffs, here and makeNrrd
 * written by Lisa Polzer
 */
 
//TODO: look at "FutureDev:" //FutureDev: produce a debugging mode excluding the cropping parts, including all the "for troubleshooting" print statements
input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";
//input_directory = "/media/user/SSD1/Athena/Data/test/";

ch0 = "488";
ch1 = "647";

directories = getFileList(input_directory);
Ndir = directories.length;

setBatchMode(true);
// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	// Find channel files inside the directory
	files = getFileList(input_directory + directories[i]);
	Array.print(files);
	Nfiles = files.length;
	print("Number of files in directory:", Nfiles);

    // Check if the directory contains any files with the word "segmented"
    contains_segmented = false;
    for (j = 0; j < Nfiles; j++) {
        if (files[j].contains("segmented") && files[j].contains(ch1)) {
            contains_segmented = true;
            break; // Stop checking once we find a "segmented" file
        }
    }

    // If no "segmented" files are found, skip this directory
    if (!contains_segmented) {
        print("Skipping directory (does not contain any 'segmented' files):", directories[i]);
        continue; // Skip to the next directory
    }

	// Find filepaths of 488 and 647 chanels
	for(j=0; j<Nfiles; j++){
		if (files[j].contains("segmented_") && files[j].contains(ch1)) {//TODO:use startswith
			file_ch1 = files[j];
			path_ch1 = input_directory + directories[i] + files[j];
		}
		if (files[j].contains("segmented_") && files[j].contains(ch1)) {
			file_ch1 = files[j];
			path_ch1 = input_directory + directories[i] + files[j];
		}
	}
	print("  ", "Channel 1:", path_ch1);
	//print("  ", "Channel 2:", path_ch1);
	
	//opens and duplicates image for use in two thresholding steps
	open(path_ch1); //print("Opening cropped highRes.tif from: " + outputDirectory + filename + "highRes_cropped.raw"); //for troubleshooting
	titleSegmented = getTitle();
	selectWindow(titleSegmented);
	
	//run connected components labelling via MLJ, save labelled image
	run("Connected Components Labeling", "connectivity=26 type=float");
	titleLabelled = substring(titleSegmented, 0, lengthOf(titleSegmented)-5) + "-lbl";
	selectWindow(titleLabelled);
	lbl_results = "labelled_" + substring(titleLabelled, 0, lengthOf(titleLabelled)-8) + ".nrrd"; //gets rid og ".tif" and "-lbl" at end
	labelled_path = input_directory + directories[i] + lbl_results; 
	run("Nrrd ... ", "nrrd=["+labelled_path+"]");

	//get information on labelled objects (sphericity, etc.), save in .csv
	run("Analyze Regions 3D", "voxel_count volume surface_area sphericity centroid max._inscribed surface_area_method=[Crofton (13 dirs.)] euler_connectivity=26");
	MLJ_suffix = "-morpho";
	MLJ_results = substring(titleSegmented, 0, lengthOf(titleSegmented)-9) + MLJ_suffix;
	selectWindow(MLJ_results);
	MLJ_results_path = input_directory + directories[i] + MLJ_results + ".csv";
	saveAs("Results", MLJ_results_path);

	//cleanup windows
	close("*");
	selectWindow(MLJ_results + ".csv");
	run("Close");

}

print("\nFinished adding MorphoLibJ labels and metrics for plaques!\n");
