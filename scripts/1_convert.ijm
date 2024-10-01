//input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";
input_directory= "/media/user/SSD1/Athena/Data/test/";

directories = getFileList(input_directory);
Ndir = directories.length;

setBatchMode(true);
// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);
	
	// Find channel files inside the directory
	files = getFileList(input_directory + directories[i]);
	Nfiles = files.length;
	print("Number of files:", Nfiles);
	if (Nfiles != 2){
		print("Number of files not equal to 2!");	
		continue;
	}
	
	// Loop over channel files
	for(j=0; j<Nfiles; j++){
		print("  ", files[j]);
		
		// Load file
		path = input_directory + directories[i] + files[j];
		print(path);
		
		open(path);
		title = getTitle();
		
		// Save as nrrd
		output_path = input_directory + directories[i] + "original_" + files[j] + ".nrrd";
		print(output_path);
		run("Nrrd ... ", "nrrd=" + output_path);
		
		// Close open files
		run("Close All");
	}
}
print("DONE.");
setBatchMode(false);
