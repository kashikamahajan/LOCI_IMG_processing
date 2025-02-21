//
// Multi-immersion bigStitcher
//

//version
version = "1.2";
//Modified by Michael Nelson to run in Win11 environment
//Functions such as "Define dataset ..." and "Fuse images ..." are not recognized

//start log
IJ.log(" ");
selectWindow("Log");
run("Close");
IJ.log("---");
IJ.log("Multi-immersion bigStitcher");
//If no downsampling was used, set these to 1. Otherwise include the amount of downsampling used in
// "Downsample 3D volumes.ijm"
preloadDownsampleX=8
preloadDownsampleY=8
preloadDownsampleZ=16
//set options
setOption("ExpandableArrays", true);
//Tile count same as file names - note that filenames start at 0
//so value here will be the highest number+1
x_tiles = 2;
y_tiles = 3; 
//Voxel size currently set for CTLSM1 at LOCI, 10x objective, default settings
x_voxel = 1.1127*preloadDownsampleX; 
y_voxel = 1.1127*preloadDownsampleY; 
z_voxel = 2.5*preloadDownsampleZ; 
//Should reduce this in the future.
overlap_x=25;
overlap_y=25;
//need to prompt user, give defualts, and add overlap

//get path and generate list of stacks
IJ.log("-");
IJ.log("Waiting for user input...");
basepath = getDirectory("Select a folder");
//basepath = "C:/ImageAnalysis/MikeNelson/20250122_140221_012125_mpeg1647_propI_2.2yrs_F/downsample"

if (!endsWith(basepath, File.separator))
{
    basepath = basepath + File.separator;
}

//OLD SETTINGS - For WIN10 and old light sheet
//run("Define dataset ...", 
//"define_dataset=[Automatic Loader (Bioformats based)] project_filename=dataset.xml path=" + basepath + "*.tif exclude=100"+
//" pattern_0=Tiles pattern_1=Tiles pattern_2=Channels pattern_3=Illuminations modify_voxel_size? "+
//"voxel_size_x="+x_voxel+" voxel_size_y="+y_voxel+" voxel_size_z="+z_voxel+" voxel_size_unit=µm move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)]"+
//"grid_type=[Up & Right] tiles_x="+ x_tiles +" tiles_y=" +y_tiles +" tiles_z=1 overlap_x_(%)="+ overlap_x +" overlap_y_(%)="+ overlap_y +" overlap_z_(%)=0 "+
//"keep_metadata_rotation how_to_load_images=[Re-save as multiresolution HDF5] dataset_save_path="+ basepath +" subsampling_factors=[{ {1,1,1}, {2,2,1}, {4,4,1}, {8,8,1} }] "+
//"hdf5_chunk_sizes=[{ {64,64,1}, {64,32,2}, {32,32,4}, {32,32,4} }] timepoints_per_partition=1 setups_per_partition=0 use_deflate_compression export_path=" + basepath + "dataset");

run("Define Multi-View Dataset", "define_dataset=[Automatic Loader (Bioformats based)]"+
" project_filename=dataset.xml path=" + basepath +
" exclude=100 pattern_0=Tiles pattern_1=Tiles pattern_2=Channels"+
" move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)] grid_type=[Up & Right]"+
" tiles_x="+ x_tiles +" tiles_y=" +y_tiles +" tiles_z=1 overlap_x_(%)="+ overlap_x +" overlap_y_(%)="+ overlap_y +" overlap_z_(%)=10 keep_metadata_rotation"+
" how_to_store_input_images=[Re-save as multiresolution HDF5] load_raw_data_virtually"+
" metadata_save_path="+ basepath +
" image_data_save_path="+ basepath +" check_stack_sizes"+
" subsampling_factors=[{ {1,1,1} }] hdf5_chunk_sizes=[{ {16,16,16} }] timepoints_per_partition=1 setups_per_partition=0 use_deflate_compression "+
"export_path=" + basepath + "dataset");



run("Calculate pairwise shifts ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] method=[Phase Correlation] channels=[Average Channels] downsample_in_x=1 downsample_in_y=1 downsample_in_z=1");

run("Filter pairwise shifts ...", "select=" + basepath + "dataset.xml filter_by_link_quality min_r=.7 max_r=1 max_shift_in_x=0 max_shift_in_y=0 max_shift_in_z=0 max_displacement=0");

run("Optimize globally and apply shifts ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] relative=2.500 absolute=3.500 global_optimization_strategy=[Two-Round using metadata to align unconnected Tiles] fix_group_0-0,");

//run("ICP Refinement ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] icp_refinement_type=[Simple (tile registration)] downsampling=[Downsampling 8/8/4] interest=[Average Threshold] icp_max_error=[Normal Adjustment (<5px)]");

//Windows10
//run("Fuse dataset ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[Currently Selected Views] downsampling=2 pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation] image=[Virtual] interest_points_for_non_rigid=[-= Disable Non-Rigid =-] blend preserve_original produce=[Each timepoint & channel] fused_image=[Save as (compressed) TIFF stacks]"+
//" output_file_directory="+ basepath +" filename_addition=[]");

//Windows11
run("Image Fusion", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[Currently Selected Views] downsampling=2 pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation] image=[Virtual] interest_points_for_non_rigid=[-= Disable Non-Rigid =-] blend preserve_original produce=[Each timepoint & channel] fused_image=[Save as (compressed) TIFF stacks]"+
" output_file_directory="+ basepath +" filename_addition=[]");
//changed to virtual image