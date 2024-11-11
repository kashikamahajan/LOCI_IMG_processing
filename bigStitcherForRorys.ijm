//
// Multi-immersion bigStitcher
//

//version
version = "1.1";

//start log
IJ.log(" ");
selectWindow("Log");
run("Close");
IJ.log("---");
IJ.log("Multi-immersion bigStitcher");

//set options
setOption("ExpandableArrays", true);
x_tiles = 2;//opposite of rory's nomenclature
y_tiles = 5; 

x_voxel = 2.375; 
y_voxel = 2.375; 
z_voxel = 10; 
//need to prompt user, give defualts, and add overlap

//get path and generate list of stacks
IJ.log("-");
IJ.log("Waiting for user input...");
basepath = getDirectory("Select a folder");


run("Define dataset ...", "define_dataset=[Automatic Loader (Bioformats based)] project_filename=dataset.xml path=" + basepath + "*.tif exclude=100 pattern_0=Tiles pattern_1=Channels pattern_2=Illuminations modify_voxel_size? voxel_size_x="+x_voxel+" voxel_size_y="+y_voxel+" voxel_size_z="+z_voxel+" voxel_size_unit=µm move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)] grid_type=[Up & Right] tiles_x="+x_tiles+" tiles_y="+y_tiles+" tiles_z=1 overlap_x_(%)=21 overlap_y_(%)=21 overlap_z_(%)=0 keep_metadata_rotation how_to_load_images=[Re-save as multiresolution HDF5] dataset_save_path="+ basepath +" subsampling_factors=[{ {1,1,1}, {2,2,1}, {4,4,1}, {8,8,1} }] hdf5_chunk_sizes=[{ {64,64,1}, {64,32,2}, {32,32,4}, {32,32,4} }] timepoints_per_partition=1 setups_per_partition=0 use_deflate_compression export_path=" + basepath + "dataset");

run("Calculate pairwise shifts ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] method=[Phase Correlation] channels=[Average Channels] downsample_in_x=1 downsample_in_y=1 downsample_in_z=1");

run("Filter pairwise shifts ...", "select=" + basepath + "dataset.xml filter_by_link_quality min_r=.7 max_r=1 max_shift_in_x=0 max_shift_in_y=0 max_shift_in_z=0 max_displacement=0");

run("Optimize globally and apply shifts ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] relative=2.500 absolute=3.500 global_optimization_strategy=[Two-Round using Metadata to align unconnected Tiles] fix_group_0-0,");

//run("ICP Refinement ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] icp_refinement_type=[Simple (tile registration)] downsampling=[Downsampling 8/8/4] interest=[Average Threshold] icp_max_error=[Normal Adjustment (<5px)]");

run("Fuse dataset ...", "select=" + basepath + "dataset.xml process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[Currently Selected Views] downsampling=2 pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation] image=[Virtual] interest_points_for_non_rigid=[-= Disable Non-Rigid =-] blend preserve_original produce=[Each timepoint & channel] fused_image=[Save as (compressed) TIFF stacks] output_file_directory="+ basepath +" filename_addition=[]");
//changed to virual image