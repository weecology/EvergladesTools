from deepforest import main
import os

def evaluate(model, test_csv):
    """Evaluate a model on labeled images.
    
    Args:
        model (main.deepforest): A trained deepforest model.
        test_csv (str): The path to a CSV file containing annotations. Images are assumed to be in the same directory
    Returns:
        dict: A dictionary of evaluation metrics.
    """
    model.config["validation"]["csv_file"] = test_csv
    model.config["validation"]["root_dir"] = os.path.dirname(test_csv)
    results = model.trainer.validate(model)

    return results

def load(path):
    """Load a trained model from disk.
    
    Args:
        path (str): The path to a model checkpoint.
    
    Returns:
        main.deepforest: A trained deepforest model.
    """

    return main.deepforest.load_from_checkpoint(path)

def train(annotations, image_paths):
    """Train a model on labeled images.
    
    Args:
        image_paths (list): A list of image paths.
    
    Returns:
        main.deepforest: A trained deepforest model.
    """
    
    model = main.deepforest.deepforest()
    model.train(image_paths)
    
    return model