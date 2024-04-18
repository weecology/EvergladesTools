import tqdm, tqdm.notebook
tqdm.tqdm = tqdm.notebook.tqdm  # notebook-friendly progress bars
from pathlib import Path

from hloc import extract_features, match_features, reconstruction, visualization, pairs_from_exhaustive, triangulation
from hloc.visualization import plot_images, read_image
from hloc.utils import viz_3d
import os
import pycolmap
from hloc.localize_sfm import QueryLocalizer, pose_from_cluster, main
import torch
import pandas as pd
import torchvision

def create_sfm_model(image_dir, output_path, image_paths=None, feature_type="disk", matcher="disk+lightglue", visualize=False):
  """
  Generate features for a set of images and perform matching.

  Args:
    image_dir (Path): Path to the directory containing the input images.
    image_paths (Optional, list): List of paths to the input images. Can be a subset of the images in the directory.
    output_path (Path): Path to the output directory.
    feature_type (str, optional): Type of feature extraction method. Defaults to "disk".
    matcher (str, optional): Type of feature matching method. Defaults to "disk+lightglue".
    visualize (bool, optional): Whether to visualize the SfM model. Defaults to False.

  Returns:
    None
  """
  sfm_pairs = output_path / 'pairs-sfm.txt'
  loc_pairs = output_path / 'pairs-from-sfm.txt'
  sfm_dir = output_path / 'sfm'
  features = output_path / 'features.h5'
  matches = output_path / 'matches.h5'
  results = output_path / 'results.txt'
  reference_sfm = output_path / "sfm_superpoint+superglue"  # the SfM model we will build

  # Set feature type
  feature_conf = extract_features.confs[feature_type]
  matcher_conf = match_features.confs[matcher]

  # List and view images
  images = [read_image(image_dir / x) for x in image_paths]
  plot_images(images, dpi=200)

  # Match and write files to disk
  if not os.path.exists(features):
    extract_features.main(conf=feature_conf, image_dir=image_dir, image_list=image_paths, feature_path=features)
  if not os.path.exists(sfm_pairs):
    pairs_from_exhaustive.main(sfm_pairs, image_list=image_paths)
  if not os.path.exists(matches):
    match_features.main(matcher_conf, sfm_pairs, features=features, matches=matches)
  if os.path.exists(sfm_dir):
    model = reconstruction.main(sfm_dir = sfm_dir, image_dir=image_dir, pairs=sfm_pairs, features=features, matches=matches)
  
  if visualize:
    visualization.visualize_sfm_2d(model, image_dir, color_by="visibility", n=1)

  return model


def align_prediction(predictions, model):
  """Align the predictions to the SfM model."""

  # Convert pandas df to boxes

  # Multiply each box by the camera matrix

  # Recreate the pandas df with the new boxes

  pass

  return aligned_prediction

def align_and_delete(model, predictions, threshold=0.5):
  """
  Given a set of images and predictions, align the images using the sfm_model and delete overlapping images.

  Args:
    model (SfMModel): The SfM model containing the images.
    predictions (DataFrame): The predictions dataframe containing the bounding box predictions.
    threshold (float, optional): The threshold value for non-max suppression. Defaults to 0.5.

  Returns:
    DataFrame: The filtered predictions dataframe after aligning and deleting overlapping images.
  """
  # Load the SfM model  
  references_registered = [model.images[i].name for i in model.reg_image_ids()]
  image_names = predictions.image_path.unique()

  for image_name in image_names:
    references_registered = [model.images[i].name for i in model.reg_image_ids()]
    image_index = references_registered.index(image_name)
    image = model.images[image_index]
    image_names = predictions.image_path.unique()
    camera_matrix = image.camera.projection_matrix
  
    # Align the predictions
    aligned_predictions = align_prediction(predictions, camera_matrix)

    # Perform non-max suppression on aligned predictions
    # Convert bounding box coordinates to torch tensors
    boxes = torch.tensor(aligned_predictions[['xmin', 'ymin', 'xmax', 'ymax']].values)

    # Convert scores to torch tensor
    scores = torch.tensor(aligned_predictions['score'].values)

    # Perform non-max suppression
    keep = torchvision.ops.nms(boxes, scores, threshold)

    # Filter the original dataframe based on the keep indices
    filtered_df = predictions.iloc[keep]

    return filtered_df