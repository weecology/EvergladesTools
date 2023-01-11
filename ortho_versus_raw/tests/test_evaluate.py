# test evaluate.py
import evaluate
import pytest
import os
from deepforest import main

ROOT = os.path.dirname(evaluate.__file__)
@pytest.fixture()
def model():
    model = main.deepforest() 
    model.use_bird_release()
    
    return model
    
def test_predict_tile(model):
    predictions = evaluate.predict_tile(model, tile_path="{}/tests/data/sample_tile.png".format(ROOT))
    assert not predictions.empty
    
def test_predict_images(model):
    predictions = evaluate.predict_images(model, directory="{}/tests/data/sample_tile/".format(ROOT))
    assert not predictions.empty
    
def test_compare_tiles_and_orthos(model):
    predictions = evaluate.compare_tiles_and_orthos(model, tile_paths=["{}/tests/data/sample_tile.png".format(ROOT)])
    assert not predictions[0].empty