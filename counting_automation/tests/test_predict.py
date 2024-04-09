import os
import pandas as pd
import pytest
from scripts.predict import predict
from deepforest import get_data

def test_predict(tmpdir):
    image_path = get_data('OSBS_029.png')
    save_dir = tmpdir.strpath
    predict(image_path, save_dir, model_path=None)
    basename = os.path.splitext(os.path.basename(image_path))[0]
    csv_path = os.path.join(save_dir, "{}.csv".format(basename))
    svg_path = os.path.join(save_dir, "{}.svg".format(basename))
    
    # Check if the .csv file is created
    assert os.path.exists(csv_path)
    # Check if the .svg file is created
    assert os.path.exists(svg_path)