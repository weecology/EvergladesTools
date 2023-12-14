import pandas as pd
from src import data, model, upload, active_learning
from deepforest import visualize
import datetime
import os
import yaml

def iterate(checkpoint_dir, images_to_annotate_dir, annotated_images_dir, test_csv, user, host, folder_name, key_filename, model_checkpoint=None, annotation_csv=None):
    """A Deepforest pipeline for rapid annotation and model iteration.

    Args:
        checkpoint_dir: The path to a directory for saving model checkpoints.
        images_to_annotate_dir: The path to a directory of images to annotate.
        annotated_images_dir: The path to a directory of annotated images.
        test_csv: The path to a CSV file containing annotations. Images are assumed to be in the same directory.
        user (str): The username for uploading images to the annotation platform.
        host (str): The host URL of the annotation platform.
        folder_name (str): The name of the folder to upload images to.
        model_checkpoint (str, optional): The path to the model checkpoint file. Defaults to None.
        annotation_csv (str, optional): The path to the CSV file containing annotations. Defaults to None. This will skip checking the server for debugging

    Returns:
        None
    """
    # Check event for there new annotations
    # Download labeled annotations
    sftp_client = upload.create_client(user=user, host=host, key_filename=key_filename)
    if annotation_csv is None:
        annotations = upload.download_annotations(sftp_client, folder_name=folder_name, annotated_images_dir=annotated_images_dir, archive=True)
        complete = data.check_if_complete(annotations)
    else:
        annotations = pd.read_csv(annotation_csv)
        complete = True
    if complete:
        # Save new training data with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        train_path = os.path.join(annotated_images_dir, "train_{}.csv".format(timestamp))
        annotations.to_csv(train_path, index=False)

        # Load existing model
        if model_checkpoint:
            m = model.load(model_checkpoint)
        elif os.path.exists(checkpoint_dir):
            m = model.get_latest_checkpoint(checkpoint_dir, annotations)
        else:
            evaluation = None

        # Choose new images to annotate
        m.config["validation"]["csv_file"] = test_csv
        m.config["validation"]["root_dir"] = os.path.dirname(test_csv) 
        before_evaluation = model.evaluate(m, test_csv=test_csv)
        print(before_evaluation)

        # Train model and save checkpoint
        train_df = data.gather_data(annotated_images_dir)

        # View test images overlaps, just a couple debugs
        #visualize.plot_prediction_dataframe(df=pd.read_csv(test_csv).head(100), root_dir=os.path.dirname(test_csv), savedir="/blue/ewhite/everglades/label_studio/test_plots")
        #visualize.plot_prediction_dataframe(df=train_df.head(100), root_dir=annotated_images_dir, savedir="/blue/ewhite/everglades/label_studio/test_plots")

        #m = model.train(model=m, annotations=train_df, test_csv=test_csv, checkpoint_dir=checkpoint_dir, train_image_dir=annotated_images_dir)

        # Choose new images to annotate
        evaluation = model.evaluate(m, test_csv=test_csv)
        print(evaluation)

        # Move annotated images out of local pool
        #data.move_images(src_dir=images_to_annotate_dir, dst_dir=annotated_images_dir, annotations=annotations)

        # Remove images that have been labeled on the label_studio server
        #upload.remove_annotated_images_remote_server(sftp_client=sftp_client, annotations=annotations, folder_name=folder_name)

        # Choose local images to annotate
        images = active_learning.choose_images(image_dir=images_to_annotate_dir, evaluation=None, strategy="random", n=3)

        # Predict images
        preannotations = model.predict(m, images)
        
        # Upload images to annotation platform
        upload.upload_images(sftp_client=sftp_client, images=images, folder_name=folder_name)
        upload.upload_preannotations(sftp_client=sftp_client, preannotations=preannotations, images=images, folder_name=folder_name, images_to_annotate_dir=images_to_annotate_dir)

if __name__ == "__main__":
    # Read config from pipeline_config.yml
    config = yaml.safe_load(open("Airplane/pipeline_config.yml"))
    
    iterate(
        checkpoint_dir="/blue/ewhite/everglades/label_studio/checkpoints",
        images_to_annotate_dir=config["images_to_annotate_dir"],
        annotated_images_dir=config["annotated_images_dir"],
        model_checkpoint=config["model_checkpoint"],
        user=config["user"],
        host=config["server_url"],
        test_csv=config["test_csv"],
        folder_name=config["folder_name"],
        key_filename=config["key_filename"],
        annotation_csv=config["annotation_csv"]
        )

