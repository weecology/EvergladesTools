from scripts.stitching import create_sfm_model, align_and_delete
from scripts.predict import predict
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
    
def test_align_and_delete():
    test_data_dir = os.path.join(os.path.dirname(__file__),"data")
    image_paths = glob.glob(os.path.join(test_data_dir, "*.JPG"))
    predictions = predict(image_paths, save_dir=None, model_path=None)
    image_dir = Path(test_data_dir)
    output_path = Path(os.path.join(test_data_dir, "output"))
    model = create_sfm_model(image_dir=image_dir, image_paths=image_paths, output_path=output_path)
    unique_predictions = align_and_delete(predictions, model=model)