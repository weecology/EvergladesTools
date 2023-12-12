from logging import warn
from deepforest import main
import os
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import CometLogger
import tempfile
import warnings

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

def load(path, annotations):
    """Load a trained model from disk.
    
    Args:
        path (str): The path to a model checkpoint.
    
    Returns:
        main.deepforest: A trained deepforest model.
    """
    # Check classes
    snapshot = main.deepforest.load_from_checkpoint(path)
    classes = len(annotations["label"].unique())
    if snapshot.num_classes != classes:
        warnings.warn("The number of classes in the model does not match the number of classes in the annotations. The backbone will be extracted and retrained.")
        label_dict = {value: index for index, value in enumerate(annotations.label.unique())}
        m = main.deepforest(num_classes=classes, label_dict=label_dict)
        m.model.backbone.load_state_dict(snapshot.model.backbone.state_dict())
        m.model.head.regression_head.load_state_dict(snapshot.model.head.regression_head.state_dict())
    else:
        m = snapshot

    return m

def train(model, annotations, test_csv, train_image_dir, checkpoint_dir):
    """Train a model on labeled images.
    Args:
        image_paths (list): A list of image paths.
    
    Returns:
        main.deepforest: A trained deepforest model.
    """
    tmpdir = tempfile.gettempdir()
    comet_logger = CometLogger(project_name="everglades-species", workspace="weecology")
    comet_logger.experiment.log_table("train.csv", annotations)

    annotations.to_csv(os.path.join(tmpdir,"train.csv"), index=False)
    model.config["train"]["csv_file"] = os.path.join(tmpdir,"train.csv")
    model.config["train"]["root_dir"] = train_image_dir
    model.config["validation"]["csv_file"] = test_csv
    model.config["validation"]["root_dir"] = os.path.dirname(test_csv) 
    
    checkpoint_callback = ModelCheckpoint(dirpath=checkpoint_dir)
    model.create_trainer(callbacks=[checkpoint_callback])
    model.trainer.fit(model)

    return model