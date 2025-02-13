/*
 * ImageJ Macro to automate large 3D data pre-processing.
 * 
 * Requires the N5 Update Site.
 * Install via: Help -> Update -> Manage Update Sites -> Choose N5 -> Apply Changes.
 * 
 * Expects all data to be inside the same folder.
 * If there are multiple channels, they are expected to be in different .tif/.tiff files, 
 */

macro "Preprocess and Crop Large TIFFs" {
    getUserInputs();
    processFiles();
    print("Processing complete!");
}

// Global variables
var inputDir, Nchannels, channels, doCrop, doFlip, doPixelSize, pixelX, pixelY, pixelZ, outputFormat, outputDir;

function getUserInputs() {
	
	// Dialog
    Dialog.create("Preprocessing Parameters");
    
    Dialog.addDirectory("Select Data Directory:", "/Users/athena/Documents/FILES/4_LAB_UZH_Aguzzi/1_CODES/SleepBrains/scripts/pre-process/test");
    
    Dialog.addNumber("Number of data channels:", 2);
    Dialog.addString("Space-separated channel identifiers", "488 647");
    
    Dialog.addCheckbox("Perform x/y/z crop ?", true);
    Dialog.addCheckbox("Perform stack flips ?", true);
    Dialog.addCheckbox("Adjust Pixel Properties ?", true);
    Dialog.addNumber("Pixel size in X (um):", 3.26);
    Dialog.addNumber("Pixel size in Y (um):", 3.26);
    Dialog.addNumber("Pixel size in Z (um):", 3.00);
    
    Dialog.addChoice("Output format:", newArray("nrrd"), "nrrd");
    Dialog.addDirectory("Select Output Directory:", "default");
    Dialog.show();

	// Parse dialog options
    inputDir = Dialog.getString();
    Nchannels = Dialog.getNumber();
    channels_string = Dialog.getString();
    channels = split(channels_string, " ");
    if (Nchannels != channels.length) {
    	exit("Error: List of provided channels does not correspond to number of channels.");
    }
    doCrop = Dialog.getCheckbox();
    doFlip = Dialog.getCheckbox();
    doPixelSize = Dialog.getCheckbox();
    pixelX = Dialog.getNumber();
    pixelY = Dialog.getNumber();
    pixelZ = Dialog.getNumber();
    outputFormat = Dialog.getChoice();
    outputDir = Dialog.getString();    
    
    // Print parsed variables
    print("Input directory:", inputDir);
    print("Number of channels:", Nchannels);
    for (i = 0; i < Nchannels; i++) {
    	print("  ", channels[i]);
    }
    print("Crop:", doCrop);
    print("Flip:", doFlip);
    print("Set pixel size:", doPixelSize);
    if (doPixelSize) {
    	print("  x:", pixelX);
    	print("  y:", pixelY);
    	print("  z:", pixelZ);
    }
    print("Output format:", outputFormat);
    print("Output directory:", outputDir);

    
    exit();
}

function processFiles() {
    list = getFileList(inputDir);
    
    if (list.length == 0) {
        print("No files found in the directory.");
        return;
    }
    else {
		print("Found ", list.length, " tif/tiff files in the directory.");
    }
    
    // Loop over all .tif/.tiff files
    for (i = 0; i < list.length; i++) {
        if (!endsWith(list[i], ".tif") && !endsWith(list[i], ".tiff")) {
            print("Skipping non-TIFF file: " + list[i]);
            continue;
        }
        path = inputDir + File.separator + list[i];
        print("Processing: " + path);
        
        open(path);
        
        crop_and_flip();
        setVoxelSize(pixelX, pixelY, pixelZ, "micron");
        saveImage(list[i]);
    	close("*");;
    }
}

function crop_and_flip() {
	
	// xy-cropping
	setTool("rectangle");
	waitForUser("xy-Cropping", "Select cropping region. Note slices to keep for z-cropping.\nPress 'OK' when done.");
	getSelectionBounds(x, y, w, h);
	run("Crop");
    
	// z-cropping
	Dialog.create("z-Cropping");
	Dialog.addNumber("First Slice:",1);
	Dialog.addNumber("Last Slice:",nSlices);
	Dialog.show();
	z1 = parseInt(Dialog.getNumber());
    z2 = parseInt(Dialog.getNumber());
	run("Slice Keeper", "first=" + z1 + " last=" + z2 + " increment=1");
	
	// FLIPPING: Flip stack to match orientation of Allen Brain Atlas.
	// depth and horizontal flipping
	Dialog.create("Options for stack flipping");
	Dialog.addNumber("Give 1 to flip z-stack, 0 to NOT flip:",0);
	Dialog.addNumber("Give 1 to flip horizontally, 0 to NOT flip:",0);
	Dialog.show();
	flipZ = parseInt(Dialog.getNumber());
	flipH = parseInt(Dialog.getNumber());
	if(flipZ==1){
		run("Flip Z");
	}
	if(flipH==1){
		run("Flip Horizontally", "stack");
	}
	
	// Saving cropping info in file
	correctionsInfo_path = input_directory + directories[i] + "cropping_info.txt";
	print(correctionsInfo_path);
	correctionsInfo = File.open(correctionsInfo_path);
	print(correctionsInfo, "filename\t\tx0\t\ty0\t\twidth\t\theight\t\tfirstSlice\t\tlastSlice\t\tflipZ\t\tflipH");
	print(correctionsInfo, file_ch0+"\t\t"+x+"\t\t"+y+"\t\t"+width+"\t\t"+height+"\t\t"+firstSlice+"\t\t"+lastSlice+"\t\t"+flipZ+"\t\t"+flipH);
	File.close(correctionsInfo);
}

function saveImage(path) {
    baseName = File.getNameWithoutExtension(path);
    savePath = outputDir + File.separator + baseName + "." + outputFormat;
    if (outputFormat == "nrrd") {
    	run("Nrrd ... ", "nrrd=" + savePath);
    } else {
        exit("Error. Only nrrd is available as saving option.");
    }
    close();
    print("Saved: " + savePath);
}
