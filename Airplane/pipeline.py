from src import data, model, predict, upload

def iterate(image_dir, test_csv, user, host, folder_name, model_checkpoint=None):
    """A Deepforest pipeline for rapid annotation and model iteration.

    Args:
        image_dir: The path to a directory of images to annotate.
        test_csv: The path to a CSV file containing annotations.
        user (str): The username for uploading images to the annotation platform.
        host (str): The host URL of the annotation platform.
        folder_name (str): The name of the folder to upload images to.
        model_checkpoint (str, optional): The path to the model checkpoint file. Defaults to None.

    Returns:
        None
    """
    # Load existing model
    if model_checkpoint:
        m = model.load(model_checkpoint)
        evaluation = model.evaluate(m)
    else:
        evaluation = None

    # Choose images
    images = data.choose_images(image_dir, evaluation)

    # Predict images
    predicted_images = predict.predict(model, images)

    # Upload images to annotation platform
    upload.upload_images(predicted_images, user, host, folder_name)

    # Check event for complete? 
    complete = data.check_if_complete()
    if complete:
        # Download labeled annotations
        annotations = data.download_annotations()

        # Move images out of pool
        data.move_images(annotations)

        # Remove images that have been labeled
        #upload.remove_annotated_images(annotations)

        # Train model
        model = model.train(annotations)

        # Save model
        model.save("model_checkpoint.pkl")

if __name__ == "__main__":
    server_url = 'serenity.ifas.ufl.edu'
    folder_name = '/pgsql/retrieverdash/everglades-label-studio/everglades-data/input'
    model_checkpoint = "/blue/ewhite/everglades/Zooniverse//20220910_182547/species_model.pl"
    test_csv = "/blue/ewhite/everglades/Zooniverse/cleaned_test/test_resized.csv"
    iterate(image_dir="/blue/ewhite/everglades/label_studio/",model_checkpoint=model_checkpoint, user="ben",host=server_url, folder_name=folder_name)

