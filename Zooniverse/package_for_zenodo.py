# Find the matching shp for each image for everglades data
import os
import glob
import pandas as pd
import zipfile

base_folder = "/orange/ewhite/everglades/Zooniverse/parsed_images"

# Find all shp files
shp_files = glob.glob(os.path.join(base_folder, "*.shp"))

# Find all .png files
png_files = glob.glob(os.path.join(base_folder, "*.png"))

# Match the shp files to the png files
shp_png = []
for shp_file in shp_files:
    shp_name = os.path.basename(shp_file)
    png_name = shp_name.replace(".shp", ".png")
    if os.path.join(base_folder, png_name) in png_files:
        shp_png.append((shp_name, png_name))

# Print the number of unique files
print("There are {} matched images".format(len(shp_png)))

# Read in train and test csvs
train = pd.read_csv(os.path.join(base_folder, "train.csv"))
test = pd.read_csv(os.path.join(base_folder, "test.csv"))

# Unique images in train and test
print("There are {} images in train".format(len(train.image_path.unique())))
print("There are {} images in test".format(len(test.image_path.unique())))

# Make sure all images are in the shp_png
for image in train.image_path.unique():
    if not any(image in png for shp, png in shp_png):
        print("Missing image in train: {}".format(image))

# Add the shapefiles to the zip
zip_file = zipfile.ZipFile(os.path.join(base_folder, "zenodo_upload.zip"), "w",)
for shp, png in shp_png:
    zip_file.write(os.path.join(base_folder, png), png)

# Add all the empty frames
empty_frames = pd.read_csv(os.path.join(base_folder, "empty_frames.csv"))
for empty_frame in empty_frames.image_path:
    zip_file.write(os.path.join(base_folder, empty_frame), empty_frame)
    
# Add the train and test csvs to the zip
zip_file.write("train.csv", "train.csv")
zip_file.write("test.csv", "test.csv")
zip_file.write("empty_frames.csv", "empty_frames.csv")


zip_file.close()

