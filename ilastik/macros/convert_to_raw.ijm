//input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/test_ilastik/";
input_directory = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/ilastik/";

files = getFileList(input_directory);
Nfiles = files.length;
for (i=0; i<Nfiles; i++) {
	if (files[i].startsWith("cropped_original_Brain")) {
		print(files[i]);

		open(input_directory + files[i]);
		
		title = files[i];
		basename = title.substring(0,lengthOf(title)-5);  // currently ends in .nrrd

		// get data dimensions
		X = getWidth();
		Y = getHeight();
		Z = nSlices;
		print(X, Y, Z);

		outname = toString(Z) + "-" + toString(Y) + "-" + toString(X) + "-uint16_" + basename + ".raw";
		print(outname);
		
		// Save as .tif
		File.makeDirectory(input_directory + "ilastik/");
		outpath = input_directory + "ilastik/" + outname;
		print(outpath);
		
		// ilastik requires .raw data to be stored in the format:
		// -  Z-Y-X-uint16_ANYTHING.raw
		// -  and the data to be in Intel Byte format !! Check box in Edit->Options->Input/Output
		
		// Choose Intel byte format for data saving
		run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file save copy_row save_column save_row");
		
		saveAs("Raw Data", outpath);
		
		close("*");
	}
}
