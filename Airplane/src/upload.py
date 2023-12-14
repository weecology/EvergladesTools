import paramiko
import os
from src import data
import pandas as pd
import glob
import tempfile
def create_client(user, host, key_filename):
    # Download annotations from Label Studio
    # SSH connection with a user prompt for password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, key_filename=key_filename)
    sftp = ssh.open_sftp()

    return sftp

def upload_preannotations(sftp_client, preannotations, images_to_annotate_dir, folder_name):
    """Upload preannotations to the Label Studio server.
    Args:
        preannotations (list): A list of preannotations.
        images_to_annotate_dir (str): The path to a directory of images.
        folder_name (str): The name of the folder to upload images to.
    Returns:

    """
    # Create a temporary directory for saving JSON files
    tmpdir = tempfile.gettempdir()

    for image in preannotations:
        json_string = data.create_label_studio_json(local_image_dir=images_to_annotate_dir, remote_image_dir=folder_name, preannotations=preannotations)
        # save json and send it to label studio using scp   
        fn = "{}.json".format(os.path.splitext(os.path.basename(image.image_path.unique()[0]))[0])
        with open(os.path.join(tmpdir, fn), "w") as f:
            f.write(json_string)   
        sftp_client.put(os.path.join(tmpdir, fn), os.path.join(folder_name, "input", fn))

def upload_images(sftp_client, images, folder_name):
    # SCP file transfer
    for image in images:
        sftp_client.put(image, os.path.join(folder_name,"input",os.path.basename(image)))
        print(f"Uploaded {image} successfully")

def download_annotations(sftp_client, folder_name, annotated_images_dir, archive=False):
    """Download annotations from the Label Studio server.
    Args:
        archive (bool, optional): Whether to move the annotations from the server to archive folder. Defaults to False.

    Returns:
        pandas.DataFrame: A DataFrame of annotations.
    """
    # Download all JSON files in the annotated_images_dir folder
    remote_annotation_path = os.path.join(folder_name, "output")

    # Download all JSON files in the annotated_images_dir folder
    for file in sftp_client.listdir(remote_annotation_path):
        remote_path = os.path.join(remote_annotation_path, file)
        local_path = os.path.join(annotated_images_dir, file)
        sftp_client.get(remote_path, local_path)

        if archive:
            # Archive annotations using SSH
            archive_annotation_path = os.path.join(folder_name, "archive")
            # sftp check if dir exists
            try:
                sftp_client.listdir(archive_annotation_path)
            except FileNotFoundError:
                raise FileNotFoundError("The archive directory {} does not exist.".format(archive_annotation_path))
            # Need sudo to move files
            sftp_client.rename(remote_path, os.path.join(archive_annotation_path, file))

    # Loop through downloaded JSON files and convert them to dataframes
    annotations = []
    json_glob = os.path.join(annotated_images_dir, "*.json")
    json_files = list(glob.glob(json_glob))
    for x in json_files:        
        result = data.convert_json_to_dataframe(x)
        if result is None:
            continue
        else:
            # Confirm the image exists
            try:
                sftp_client.stat(os.path.join(folder_name,"input",result.image_path.unique()[0]))
            except FileNotFoundError:
                print("There was a json file for, but no input file for {}".format(result.image_path.unique()[0]))
                continue

            annotations.append(result)
    annotations = pd.concat(annotations)

    #Remove helper classes
    annotations = annotations[~(annotations.label=="Help me!")]
    annotations.loc[annotations.label=="Unidentified White","label"] = "Unknown White"

    return annotations

def remove_annotated_images_remote_server(sftp_client, annotations, folder_name):
    """Remove images that have been annotated on the Label Studio server."""
    # Delete images using SSH
    for image in annotations.image_path.unique():
        remote_path = os.path.join(folder_name, "input", os.path.basename(image))
        # Archive annotations using SSH
        archive_annotation_path = os.path.join(folder_name, "archive", os.path.basename(image))
        # sftp check if dir exists
        try:
            sftp_client.listdir(os.path.join(folder_name, "archive"))
        except FileNotFoundError:
            raise FileNotFoundError("The archive directory {} does not exist.".format(os.path.join(folder_name, "archive")))
        
        sftp_client.rename(remote_path, archive_annotation_path)
        print(f"Archived {image} successfully")

