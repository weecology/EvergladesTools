#Tests for converting photoshop to deepforest annotations
import pytest
import glob
import tempfile
from generate_data import *
import pandas as pd

image_pool = glob.glob("*.tif")
base_dir = tempfile.TemporaryDirectory()
paths = ["Joule_03_14_2022_crop.csv"]
df = run(paths, image_pool=image_pool, base_dir=base_dir.name)
