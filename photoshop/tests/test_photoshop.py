#Tests for converting photoshop to deepforest annotations
import pytest
import glob
import tempfile
import generate_data
import generate_empty_annotations

def test_generate_data():
    image_pool = glob.glob("*.tif")
    base_dir = tempfile.TemporaryDirectory()
    paths = ["/Users/benweinstein/Documents/EvergladesTools/photoshop/tests/Joule_03_14_2022_crop.csv"]
    df = generate_data.run(paths, image_pool=image_pool, base_dir=base_dir.name)

def test_generate_empty():
    image_pool = glob.glob("*.tif")
    base_dir = tempfile.TemporaryDirectory()
    paths = ["/Users/benweinstein/Documents/EvergladesTools/photoshop/tests/Joule_03_14_2022_crop.csv"]
    df = generate_empty_annotations.run(paths, image_pool=image_pool, base_dir=base_dir.name)