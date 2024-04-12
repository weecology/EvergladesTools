from scripts.stitching import stitch_images
import cv2
import os
import glob

test_data_dir = os.path.join(os.path.dirname(__file__),"data")

def test_stitch_images():
    # Load test images
    image_paths = glob.glob(os.path.join(test_data_dir, "*.JPG"))
    image_paths.sort()

    # Call the function
    stitch_images(image_paths)