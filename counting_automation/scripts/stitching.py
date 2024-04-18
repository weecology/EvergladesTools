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

def localize_image(model, image_dir, query_image_name, output_path):
  """
  Localize an image in a SfM model.

  Args:
    model (pycolmap.Reconstruction): The SfM model.
    image_dir (str): The directory path where the images are located.
    model_path (str): The reconstruction path to the SfM model.
    query_image_name (str): The name of the query image to be localized. Relative path
    output_path (str): The path to save the output.
    pairs (list, optional): A list of image pairs to use for localization. Defaults to None.

  Returns:
    None

  """
  matches = output_path / 'matches.h5'
  features = output_path / 'features.h5'
  loc_pairs = output_path / 'pairs-from-sfm.txt'
  results = output_path / 'results.txt'

  references_registered = [model.images[i].name for i in model.reg_image_ids()]
  camera = pycolmap.infer_camera_from_image(image_dir / query_image_name)
  ref_ids = [model.find_image_with_name(n).image_id for n in references_registered]
  conf = {
      'estimation': {'ransac': {'max_error': 12}},
      'refinement': {'refine_focal_length': True, 'refine_extra_params': True},
  }
  localizer = QueryLocalizer(model, conf)
  ret, log = pose_from_cluster(localizer, query_image_name, camera, ref_ids, features, matches)

  visualization.visualize_loc(
    results, image_dir, reconstruction, n=1, top_k_db=1, prefix="query/night", seed=2
)

def align_prediction(predictions, camera_matrix):
  pass
  return aligned_predictions

def align_and_delete(model, query_images, predictions, threshold=0.5):
  """Given a set of images and predictions, align the images using the sfm_model and delete overlapping images."""
  # Load the SfM model  
  for query_image in query_images:
    camera_matrix = localize_image(model, query_image)
    
    # Align the predictions
    aligned_predictions = align_prediction(predictions, camera_matrix)

    #Perform non-max suppression on aligned predictions
    # Convert bounding box coordinates to torch tensors
    boxes = torch.tensor(predictions[['xmin', 'ymin', 'xmax', 'ymax']].values)

    # Convert scores to torch tensor
    scores = torch.tensor(predictions['score'].values)

    # Perform non-max suppression
    keep = torchvision.ops.nms(boxes, scores, threshold)

    # Filter the dataframe based on the keep indices
    filtered_df = predictions.iloc[keep]