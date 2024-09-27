#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 07:46:01 2019

@author: rpower
"""

"""

Edited for LOCI, September 2024

"""

#from curses import resize_term
from pickle import FALSE
import numpy as np
import os
import sys
import shutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from matplotlib import pyplot as plt
from tifffile import imsave, imread
from PIL import Image

#Upcoming Tasks
#   ~Resizing images



plt.close('all')

# CHOOSE STEPS TO PERFORM 
MV_fuse=False
x_0=[512] #x centre for fusion of images
tif_convert=True
save_fused_stacks=True
save_processed_files=True
uint8_RGB = False
chng_CWD = False #If the user wants to use the current folder or not
crt_dnsize_fldr=False #If the user wants to have a downsized folder for demo stitching
resize_8bit=False #if the user wants to resize the 8bit images 

# PARAMETERS FOR TIF CONVERSION

bytes_between_images=4
bytes_before_images=4

chng_CWD=input('Do you want to change current working directory? Enter True or False: ')

# GENERATE FILE LIST & PARSE IMAGE DIMENSIONS FROM FILE
if chng_CWD:
    app = QApplication(sys.argv)  # Create the QApplication instance
    working_dir = QFileDialog.getExistingDirectory(None, 'Select Directory')  # Open directory dialog instead of file
    app.exit()  # Close the QApplication after selection
else:
    working_dir=os.getcwd

#CREATING A DOWNSIZE FOLDER IF USER REQUESTS
crt_dnsize_fldr=input("Do you want to create a downsize folder with 8-bit .tif files? Enter True or False: ")
if crt_dnsize_fldr == 'True':
    crt_dnsize_fldr=True
else:
    crt_dnsize_fldr=False

resize_8bit=input("Do you want to resize the 8-bit .tif files? Enter True or False: ")
if resize_8bit == 'True':
    resize_8bit=True
else:
    resize_8bit=False


if crt_dnsize_fldr:
    if os.path.exists(working_dir+'/DOWNSIZED') == False:
           os.mkdir(working_dir+'/DOWNSIZED')

#ASKING USER ON ACTIONS TO PERFORM
conv_16bit=input("Do you want to convert raw into 16-bit .tif files? Enter True or False: ")
if conv_16bit == 'True':
    conv_16bit=True
else:
    conv_16bit=False

ex_params=open(working_dir+'/Experimental Parameters.txt').read()
px_x=int(ex_params[ex_params.find('ROIStride')+len('ROIStride'):ex_params.find('ROIWidth')-1])
px_y=int(ex_params[ex_params.find('ROIWidth')+len('ROIWidth'):ex_params.find('ROIHeight')-1])
slices_z=int(ex_params[ex_params.find('Overlap Mode')+len('Overlap Mode'):ex_params.find('Planes')-1])
print(px_x,px_y,slices_z)


#MAKING A LIST OF ALL FILES IN DIRECTORY
file_names=list()
if tif_convert == True:
   file_type='.raw'
   print('file_type=.raw')

else:
   file_type='.tif'
   print('file_type=.tif')

for file in os.listdir(working_dir):
    if file.endswith(file_type) and not file.startswith('._'):
        file_name=os.path.join(working_dir, file)
        file_names.append(file_name)



#CREATING 8-BIT .TIF OF RAW FILES TO BE STORED IN 'DOWNSIZED' FOLDER
if crt_dnsize_fldr:
        
    downsize_dir=os.path.join(working_dir,'DOWNSIZED')
    img_shape = np.array((px_y,px_x,slices_z), dtype = np.uint)
    img = np.zeros(img_shape, dtype=np.uint16)

    for file in file_names:
        img=np.zeros(img_shape,dtype = np.uint16)
        # Read the 16-bit pixel data from the file
        px_data = np.fromfile(file, dtype=np.uint16)
        px_data = px_data[int(bytes_before_images/2):]
            
        for i in range(slices_z):
            i_start_index = i * (px_x * px_y + int(bytes_between_images / 2))
            i_end_index = i_start_index + (px_x * px_y)
                    
            px_data_i = px_data[i_start_index:i_end_index]
            img_i = px_data_i.reshape(px_y, px_x)
            # Store the slice in the img array
            img[:, :, i] = img_i

        #Bit-shifting to 8-bit
        img = (img >> 8).astype('uint8')

       

        print(img.size)

        # Save the 8-bit image
        bit8_file_name=file[:len(file) - len(file_type)] + '_8bit.tif'
        imsave(bit8_file_name, np.moveaxis(img,2, 0))
        shutil.move(bit8_file_name,downsize_dir)


#Resizing 8-bit
if resize_8bit:
    if os.path.exists(working_dir+'/DOWNSIZED'):
           downsize_dir=os.path.join(working_dir,'DOWNSIZED')
    file_8bit_names=list()
    for file in os.listdir(downsize_dir):
        if file.endswith('.tif') and not file.startswith('._'):
            file_8bit_name=os.path.join(working_dir, file)
            file_8bit_names.append(file_8bit_name)
            print(file_8bit_name)





# CONVERT TO 16-BIT .TIF AND MOVING TO TIFF_FILES DIRECTORY
if conv_16bit:

    #making directory to store .tif files
    if os.path.exists(working_dir+'/TIFF_FILES') == False:
           os.mkdir(working_dir+'/TIFF_FILES')
    tiff_dir=os.path.join(working_dir,'TIFF_FILES')

    img_shape = np.array((px_y,px_x,slices_z), dtype = np.uint)
    img=np.zeros(img_shape,dtype = np.uint16)
    for file in file_names:
        px_data = np.fromfile(file, dtype = np.uint16)
        px_data = px_data[int(bytes_before_images/2):]
        
        for i in range (0,slices_z):
        
            i_start_index=i*(px_x*px_y+int(bytes_between_images/2))
            i_end_index=i_start_index+(px_x*px_y)
                                          
            px_data_i=px_data[i_start_index:i_end_index]
            img_i=(px_data_i.reshape(px_y,px_x))
            
            img[:,:,i]=img_i

        #saving and storing files in assigned directory
        bit16_file_name=file[:len(file) - len(file_type)] + '.tif'
        imsave(bit16_file_name, np.moveaxis(img,2, 0))
        shutil.move(bit16_file_name,tiff_dir)
else:
    pass



# PARSE FILE NAMES FOR TIME-LAPSE, POSITIONS, CHANNELS, DIRECTIONS AND ROOT
     
i=file_name.find('t=') + len('t=')
j=file_name.find(',_position=') + len(',_position=')
k=file_name.find(',_channel=') + len(',_channel=')
l=file_name.find(',_direction=') + len(',_direction=')

print(i + j + k +l)


t=[]
pos=[]
channel=[]
direction=[]

root=file_name[0 : file_name.find('M,_') + len('M,_')]

print(root)

for file in file_names:
    t.append(int(file[i : i + 6]))
    pos.append(int(file[j : j + 4]))
    channel.append(int(file[k : k + 2]))
    direction.append(int(file[l : l + 2]))
    
t_points=np.max(t)
positions=np.max(pos)
channels=np.max(channel)
directions=np.max(direction)

# CREATE NECESSARY FOLDERS


if MV_fuse == True and directions == 2:
  
    print('MVFUSE TRUE')
                
    if os.path.exists(working_dir+'/fused') == False:
        
        os.mkdir(working_dir+'/fused')
        
    if uint8_RGB == True:
        
        if os.path.exists(working_dir+'/fused/RGB') == False:
    	  
           os.mkdir(working_dir+'/fused/RGB') 
        
    for a in range (0, positions):
        
        if os.path.exists(working_dir+'/fused/position_'+str(a+1)) == False:
        
           os.mkdir(working_dir+'/fused/position_'+str(a+1))  
            
        if uint8_RGB == True:
            
            if os.path.exists(working_dir+'/fused/RGB/position_'+str(a+1)) == False:
        
               os.mkdir(working_dir+'/fused/RGB/position_'+str(a+1))  
                
if directions == 1:
                
    if os.path.exists(working_dir+'/processed') == False:
        
        os.mkdir(working_dir+'/processed')
        
    if uint8_RGB == True:
        
        if os.path.exists(working_dir+'/processed/RGB') == False:
            os.mkdir(working_dir+'/processed/RGB') 

        
    for i in range (0, positions):
        
        if os.path.exists(working_dir+'/processed/position_'+str(i+1)) == False:
        
            os.mkdir(working_dir+'/processed/position_'+str(i+1))  
            
        if uint8_RGB == True:
            
            if os.path.exists(working_dir+'/processed/RGB/position_'+str(i+1)) == False:
            
                os.mkdir(working_dir+'/processed/RGB/position_'+str(i+1))  
                
if directions == 2 and MV_fuse==False: 
                
    if os.path.exists(working_dir+'/processed') == False:
        os.mkdir(working_dir+'/processed') 
        
    if uint8_RGB == True:
        
        if os.path.exists(working_dir+'/processed/RGB') == False:
            os.mkdir(working_dir+'/processed/RGB') 

    for a in range (0, positions):
        
        for b in range (0,directions):
        
            if os.path.exists(working_dir+'/processed/position_'+str(a+1)+'_direction_'+str(b+1)) == False:
        
                os.mkdir(working_dir+'/processed/position_'+str(a+1)+'_direction_'+str(b+1))   
                
            if uint8_RGB == True:
            
                if os.path.exists(working_dir+'/processed/RGB/position_'+str(a+1)+'_direction_'+str(b+1)) == False:
            
                    os.mkdir(working_dir+'/processed/RGB/position_'+str(a+1)+'_direction_'+str(b+1))  

if directions == 2 and MV_fuse==True and save_fused_stacks==True:
    
    for i in range (0, positions):
        
        for b in range (0,channels):
        
            if os.path.exists(working_dir+'/fused/position_'+str(i+1)+'_channel_'+str(b+1)) == False:
            
                os.mkdir(working_dir+'/fused/position_'+str(i+1)+'_channel_'+str(b+1))      
            
            

# COLORS FOR RGB DATA

if uint8_RGB == True:

    colors=[[0,1,1],[1,0,1],[1,1,0],[1,0,0],[0,1,0],[0,0,1]]
    
    def multi_channel_img_2_RGB_24(img):
        
        #TAKES A 4D (X,Y,3,CHANNELS) IMAGE AND CONVERTS TO A 3D APPROPRIATELY SCALED 3D (X,Y,3) ONE
    
        for c in range (0, img.shape[3]):
            
            if np.max(img[:,:,:,c]) > 0:
            
                img[:,:,:,c]=img[:,:,:,c]/np.max(img[:,:,:,c])
        
        img=np.sum(img,3)
        
        img=(img-np.min(img))/(np.amax(img)-np.amin(img))*255
    
        img=img.astype(np.uint8)
        
        return img  


# 4 BATCH PROCESS

if MV_fuse == True and directions == 2:
    
    if len(x_0) < positions:
        
        print('not enough positional arguments for fusion')
    
    x_values=np.linspace(1,px_x,px_x)
    y_values=np.linspace(1,px_y,px_y)
    
    X,Y=np.meshgrid(x_values,y_values)

    fused_mip=np.zeros((px_x,px_y),dtype=np.uint16)
   
    all_channel_fused_mip=np.zeros((channels,px_x,px_y),dtype=np.uint16)
    
    fused_stack=np.zeros((slices_z,px_x,px_y),dtype=np.uint16)
    
    if uint8_RGB == True:
    
        multi_channel_RGB_mip=np.zeros((px_x,px_y,3,channels))
    
else:
    
        direction_1_mip=np.zeros((px_x,px_y),dtype=np.uint16)
        
        direction_1_all_channel_mip=np.zeros((channels,px_x,px_y),dtype=np.uint16)
        
        if uint8_RGB == True:
    
            multi_channel_RGB_direction_1_mip=np.zeros((px_x,px_y,3,channels))

        if directions == 2:
    
            direction_2_mip=np.zeros((px_x,px_y),dtype=np.uint16)
            
            direction_2_all_channel_mip=np.zeros((channels,px_x,px_y),dtype=np.uint16)
            
            if uint8_RGB == True:
    
                multi_channel_RGB_direction_1_mip=np.zeros((px_x,px_y,3,channels))
                multi_channel_RGB_direction_2_mip=np.zeros((px_x,px_y,3,channels))


    # TIME POINTS
       
for i in range (0,t_points):
    
    current_t = 't=' + str(i + 1).zfill(6) + ',_'
    print(current_t)
    
    # POSITIONS

    for j in range (0,positions):
        
        current_pos = 'position=' + str(j + 1).zfill(4) + ',_'
        print(current_pos)
        
        sigmoid_steepness=0.05
        sigmoid_L=1-1/(1+np.exp(-sigmoid_steepness*(X-x_0[j])))
        sigmoid_R=1/(1+np.exp(-sigmoid_steepness*(X-x_0[j])))
        
         # CHANNELS
        
        for k in range (0, channels):
            
            current_channel = 'channel=' + str(k + 1).zfill(2) + ',_'
            print(current_channel)
            
            if uint8_RGB == True:
            
                current_color=colors[k]
            
            # DIRECTIONS
            
            if MV_fuse == True and directions == 2:

                R_file=root+current_t + current_pos + current_channel + 'direction=01.tif'
                print(R_file)
                
                R_image=imread(R_file).astype(dtype=np.uint16)
                
                R_mip=np.max(R_image,0)*sigmoid_R
                            
                R_mip=R_mip.astype(dtype=np.uint16)
                
                L_file=root+current_t + current_pos + current_channel + 'direction=02.tif'
                print(L_file)
                
                L_image=imread(L_file).astype(dtype=np.uint16)
                
                L_mip=np.max(L_image,0)*sigmoid_L
                            
                L_mip=L_mip.astype(dtype=np.uint16)
                
                # Z SLICES
                   
                for m in range (0, slices_z):
                    
                    fused_stack[m,:,:]=L_image[m,:,:]*sigmoid_L+R_image[m,:,:]*sigmoid_R
                    
                fused_mip=np.max(fused_stack,0)
                
                if uint8_RGB == True:
                
                    multi_channel_RGB_mip[:,:,0,k] = fused_mip * current_color[0]
                    multi_channel_RGB_mip[:,:,1,k] = fused_mip * current_color[1]
                    multi_channel_RGB_mip[:,:,2,k] = fused_mip * current_color[2]
                    
            if directions == 1:
                    
                direction_1_file=root+current_t + current_pos + current_channel + 'direction=01.tif'
                    
                direction_1_image=imread(direction_1_file).astype(dtype=np.uint16)
                    
                direction_1_mip=np.max(direction_1_image,0)
                    
                if uint8_RGB == True:
                
                    multi_channel_RGB_direction_1_mip[:,:,0,k] = direction_1_mip * current_color[0]
                    multi_channel_RGB_direction_1_mip[:,:,1,k] = direction_1_mip * current_color[1]
                    multi_channel_RGB_direction_1_mip[:,:,2,k] = direction_1_mip * current_color[2]                    
                    
                    
            if directions == 2 and MV_fuse==False:        
                    
                direction_1_file=root+current_t + current_pos + current_channel + 'direction=01.tif'
                direction_2_file=root+current_t + current_pos + current_channel + 'direction=02.tif'
                    
                direction_1_image=imread(direction_1_file).astype(dtype=np.uint16)
                direction_2_image=imread(direction_2_file).astype(dtype=np.uint16)
                    
                direction_1_mip=np.max(direction_1_image,0)
                direction_2_mip=np.max(direction_2_image,0)
                
                if uint8_RGB == True:
                
                    multi_channel_RGB_direction_1_mip[:,:,0,k] = direction_1_mip * current_color[0]
                    multi_channel_RGB_direction_1_mip[:,:,1,k] = direction_1_mip * current_color[1]
                    multi_channel_RGB_direction_1_mip[:,:,2,k] = direction_1_mip * current_color[2] 
                    multi_channel_RGB_direction_2_mip[:,:,0,k] = direction_2_mip * current_color[0]
                    multi_channel_RGB_direction_2_mip[:,:,1,k] = direction_2_mip * current_color[1]
                    multi_channel_RGB_direction_2_mip[:,:,2,k] = direction_2_mip * current_color[2]                 
                
            #CHANNELS
            
            if MV_fuse == True and directions == 2:  
                
                if save_fused_stacks == True:
                    
                    fused_root=working_dir+'/fused/position_' + str(j+1) + '_channel_'+ str(k+1) + '/' + os.path.split(root)[1]
                    
                    imsave(fused_root + current_t + current_pos + current_channel + 'fused.tif', fused_stack)
                                         
                all_channel_fused_mip[k,:,:]=fused_mip

                if uint8_RGB == True:  
                                   
                    RGB_mip=multi_channel_img_2_RGB_24(multi_channel_RGB_mip)
    
            if directions == 1:  
                
                direction_1_all_channel_mip[k,:,:]=direction_1_mip
                                           
                if uint8_RGB == True:  
                                   
                    RGB_direction_1_mip=multi_channel_img_2_RGB_24(multi_channel_RGB_direction_1_mip)                   
    
            if directions == 2 and MV_fuse==False: 
                
                direction_1_all_channel_mip[k,:,:]=direction_1_mip
                direction_2_all_channel_mip[k,:,:]=direction_2_mip                                                                                     
                                           
                if uint8_RGB == True:  
                                                       
                    RGB_direction_1_mip=multi_channel_img_2_RGB_24(multi_channel_RGB_direction_1_mip)
                    RGB_direction_2_mip=multi_channel_img_2_RGB_24(multi_channel_RGB_direction_2_mip)
                        
                    
        #POSITIONS
        
        if uint8_RGB == True:
            
            
            if MV_fuse == True and directions == 2:
                
                fused_RGB_root=working_dir+'/fused/RGB/position_'+str(j+1)+'/' + os.path.split(root)[1]

                imsave(fused_RGB_root + current_t +'all_channel_fused_RGB_mip.tif', RGB_mip)
                
            if directions == 1:
                
                processed_RGB_root=working_dir+'/processed/RGB/position_'+str(j+1)+'/' + os.path.split(root)[1]   
                
                imsave(processed_RGB_root + current_t +'all_channel_direction_1_RGB_mip.tif', RGB_direction_1_mip)
                
            if directions == 2 and MV_fuse==False:
                
                processed_RGB_root_dir1=working_dir+'/processed/RGB/position_'+str(j+1)+'_direction_1/' + os.path.split(root)[1]
                processed_RGB_root_dir2=working_dir+'/processed/RGB/position_'+str(j+1)+'_direction_2/' + os.path.split(root)[1]
                
                imsave(processed_RGB_root_dir1 + current_t +'all_channel_direction_1_RGB_mip.tif', RGB_direction_1_mip)
                imsave(processed_RGB_root_dir2 + current_t +'all_channel_direction_2_RGB_mip.tif', RGB_direction_2_mip)
            
    
        if save_processed_files == True:                              
    
            if MV_fuse == True and directions == 2:
                
                fused_root=working_dir+'/fused/position_'+str(j+1)+'/' + os.path.split(root)[1]
                                        
                imsave(fused_root+current_t +'all_channel_fused_mip.tif', all_channel_fused_mip)
                
            if directions == 1:
                
                processed_root=working_dir+'/processed/position_'+str(j+1)+'/' + os.path.split(root)[1]
                
                imsave(processed_root+current_t +'all_channel_direction_1_mip.tif', direction_1_all_channel_mip)
                
            if directions == 2 and MV_fuse==False: 
                
                processed_root_dir1=working_dir+'/processed/position_'+str(j+1)+'_direction_1/' + os.path.split(root)[1]
                processed_root_dir2=working_dir+'/processed/position_'+str(j+1)+'_direction_2/' + os.path.split(root)[1]
                
                imsave(processed_root_dir1+current_t +'all_channel_direction_1_mip.tif', direction_1_all_channel_mip)
                imsave(processed_root_dir2+current_t +'all_channel_direction_2_mip.tif', direction_2_all_channel_mip)



