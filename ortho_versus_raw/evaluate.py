import glob
import pandas as pd
import os

def predict_tile(model, tile_path):
    """
    Predict detections for a single raster tile
    Args:
        model: a loaded deepforest model 
        tile_path: a path to the tile to be predicted
    Returns:
        predictions: a pandas dataframe of detections and classifications
    """
    predictions = model.predict_tile(tile_path)

    return predictions

def predict_images(model, directory):
    """
    Predict detections for a set of images in a directory
    Args:
        model: a loaded deepforest model 
        tile_path: a path to the tile to be predicted
    Returns:
        predictions: a pandas dataframe of detections and classifications
    """
    dir_path_glob = os.path.join(directory, "*")
    images = glob.glob(dir_path_glob)
    predictions = []
    for image in images:
        prediction = model.predict_image(path=image)
        predictions.append(prediction)
    predictions = pd.concat(predictions)   
    
    return predictions

def compare_tiles_and_orthos(model, tile_paths): 
    """
    For a pair of raw images and a tile, predict the bird classifications and detections
    tile_paths: a list of tiles to be computed. The image directories should be named relative to the tile paths.
    """
    
    results = []
    for tile_path in tile_paths:
        # 1) Predict birds from orthophoto
        tile_predictions = predict_tile(model, tile_path)
        tile_predictions["tile_path"] = tile_path
        tile_predictions["tile_or_raw"] = "tile"
        
        # 2) Predict birds from raw images
        directory_name = os.path.splitext(os.path.basename(tile_path))[0]
        directory_path = os.path.dirname(tile_path)
        directory = "{}/{}".format(directory_path, directory_name)
        raw_predictions = predict_images(model, directory)
        raw_predictions["tile_path"] = tile_path
        raw_predictions["tile_or_raw"] = "raw"
        
        result = pd.concat([tile_predictions, raw_predictions])
        results.append(result)
    
    return results
        
        
        
        
        