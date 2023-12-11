import os
import random
import glob
import shutil
import json
import pandas as pd
from src.active_learning import active_learner

def choose_images(image_dir, evaluation=None):
    """Choose images to annotate.
    
    Args:
        pool (list): A list of image paths to choose from.
    
    Returns:
        list: A list of image paths to annotate.
    """
    pool = glob.glob(os.path.join(image_dir,"*")) # Get all images in the data directory
    
    if evaluation is None:
        chosen_images = random.sample(pool, 3)
    else:   
        active_learner(evaluation, pool, strategy="uncertainty")

    return chosen_images


def create_label_studio_json(image_url, predictions):
    """Create a JSON string for the Label Studio API.
    """
    # Prepare data dictionary
    data = {
        "image": image_url
    }

    # Prepare predictions list
    predictions_list = []
    for prediction in predictions:
        prediction_dict = {
            "result": prediction.result,
            "score": prediction.score,
            "cluster": prediction.cluster
        }
        predictions_list.append(prediction_dict)

    # Prepare final dictionary
    final_dict = {
        "data": data,
        "predictions": predictions_list
    }

    # Convert dictionary to JSON string
    json_string = json.dumps(final_dict)

    return json_string

# check_if_complete label studio images are done
def check_if_complete(annotations):
    """Check if any new images have been labeled.
    
    Returns:
        bool: True if new images have been labeled, False otherwise.
    """

    if annotations.shape[0] > 0:
        return True
    else:
        return False

# con for a json that looks like 
#{'id': 539, 'created_username': ' vonsteiny@gmail.com, 10', 'created_ago': '0\xa0minutes', 'task': {'id': 1962, 'data': {...}, 'meta': {}, 'created_at': '2023-01-18T20:58:48.250374Z', 'updated_at': '2023-01-18T20:58:48.250387Z', 'is_labeled': True, 'overlap': 1, 'inner_id': 381, 'total_annotations': 1, ...}, 'completed_by': {'id': 10, 'first_name': '', 'last_name': '', 'email': 'vonsteiny@gmail.com'}, 'result': [], 'was_cancelled': False, 'ground_truth': False, 'created_at': '2023-01-30T21:43:35.447447Z', 'updated_at': '2023-01-30T21:43:35.447460Z', 'lead_time': 29.346, 'parent_prediction': None, 'parent_annotation': None}
    
def convert_json_to_dataframe(json_file):
    # Open JSON file
    with open(json_file) as f:
        data = json.load(f)

    image = data["task"]["data"]["image"]


# Move images from images_to_annotation to images_annotated 
def move_images(annotations, src_dir, dst_dir):
    """Move images from the images_to_annotate folder to the images_annotated folder.
    
    Args:
        annotations (list): A list of annotations.
    
    Returns:
        None
    """
    images = annotations.image_path.unique()
    for image in images:
        src = os.path.join(src_dir, os.path.basename(image))
        dst = os.path.join(dst_dir, os.path.basename(image))
                           
        shutil.move(src, dst)

def gather_data(train_dir):
    train_csvs = glob.glob(os.path.join(train_dir,"*.csv"))
    df = []
    for x in train_csvs:
        df.append(pd.read_csv(x))
    df = pd.concat(df)
    df.drop_duplicates(inplace=True)
    
    return df

