from scripts.stitching import create_sfm_model, localize_image
import cv2
import os
import glob
from pathlib import Path


def test_create_sfm_model():
    test_data_dir = os.path.join(os.path.dirname(__file__),"data")
    # Load test images
    image_paths = glob.glob(os.path.join(test_data_dir, "*.JPG"))
    image_paths = [os.path.basename(x) for x in image_paths]
    image_paths.sort()

    # Call the function, create a local directory in test to save outputs
    image_dir = Path(test_data_dir)
    output_path = Path(os.path.join(test_data_dir, "output"))
    output_path.mkdir(parents=True, exist_ok=True)
    create_sfm_model(image_dir=image_dir, image_paths=image_paths, output_path=output_path)

    assert os.path.exists(output_path / "features.h5")
    assert os.path.exists(output_path / "matches.h5")
    
def test_localize_image():
    test_data_dir = os.path.join(os.path.dirname(__file__),"data")
    output_path = Path(os.path.join(test_data_dir, "output"))
    image_dir = Path(test_data_dir)
    image_paths = glob.glob(os.path.join(test_data_dir, "*.JPG"))
    query_image_path = os.path.basename(image_paths[1])
    reconstruction = output_path / 'sfm'

    model = create_sfm_model(image_dir=image_dir, image_paths=image_paths, output_path=output_path)
    localize_image(model, image_dir=image_dir, query_image_name=query_image_path, output_path=output_path)

def test_align_predictions():
    pass

def align_and_delete():
    pass
