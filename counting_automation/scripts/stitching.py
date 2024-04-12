from stitching import Stitcher
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
from stitching.feature_detector import FeatureDetector

def stitch_images(images, plot_results=True, show_seam=True, detector="sift"):
  settings = {"detector": "orb", "confidence_threshold": 0.5, "blender_type": "no"}

  stitcher = Stitcher(**settings)
  stitched_image = stitcher.stitch_verbose(images)
  
  if plot_results:
    image_data = [cv.imread(image) for image in images]
    plot_images(image_data)
    plot_image(stitched_image)

  return stitched_image

def plot_image(img, figsize_in_inches=(5,5)):
  fig, ax = plt.subplots(figsize=figsize_in_inches)
  ax.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
  plt.show()
    
def plot_images(imgs, figsize_in_inches=(5,5)):
  fig, axs = plt.subplots(1, len(imgs), figsize=figsize_in_inches)
  for col, img in enumerate(imgs):
      axs[col].imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
  plt.show()