import paramiko
import os
import subprocess
from src import data
import pandas as pd
import glob

def upload_preannotations(preannotations, user, host, folder_name):
    # Upload preannotations to label studio, first convert them to json from pandas dataframe
    json_string = data.convert_dataframe_to_json(preannotations)
    # save json and send it to label studio using scp   
    with open("preannotations.json", "w") as f:
        f.write(json_string)    
    subprocess.run(["scp", "preannotations.json", "{}@{}:{}".format(user, host, folder_name)]) 

def upload_images(images, user, host, folder_name):
    # SCP file transfer
    for image in images:
        subprocess.run(["scp", image, "{}@{}:{}".format(user, host, folder_name)])
        print(f"Uploaded {image} successfully")


def download_annotations(user, host, folder_name, password, annotated_images_dir, archive=False):
    """Download annotations from the Label Studio server.
    Args:
        archive (bool, optional): Whether to move the annotations from the server to archive folder. Defaults to False.

    Returns:
        pandas.DataFrame: A DataFrame of annotations.
    """
    # Download annotations from Label Studio
    # SSH connection with a user prompt for password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    sftp = ssh.open_sftp()

    # Download all JSON files in the annotated_images_dir folder
    remote_annotation_path = os.path.join(folder_name, "output")

    # Download all JSON files in the annotated_images_dir folder
    for file in sftp.listdir(remote_annotation_path):
        remote_path = os.path.join(remote_annotation_path, file)
        local_path = os.path.join(annotated_images_dir, file)
        sftp.get(remote_path, local_path)

        if archive:
            # Archive annotations using SSH
            archive_annotation_path = os.path.join(folder_name, "archive")
            # sftp check if dir exists
            try:
                sftp.listdir(archive_annotation_path)
            except FileNotFoundError:
                raise FileNotFoundError("The archive directory {} does not exist.".format(archive_annotation_path))
            # Need sudo to move files
            #sftp.rename(remote_path, os.path.join(archive_annotation_path, file))

    # Loop through downloaded JSON files and convert them to dataframes
    annotations = []
    json_glob = os.path.join(annotated_images_dir, "*.json")
    json_files = list(glob.glob(json_glob))
    for x in json_files:        
        result = data.convert_json_to_dataframe(x)
        if result is None:
            continue
        else:
            annotations.append(result)
    annotations = pd.concat(annotations)

    #Remove helper classes
    annotations = annotations[~(annotations.label=="Help me!")]

    return annotations

def remove_annotated_images_remote_server(annotations, user, host, folder_name, password):
    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    sftp = ssh.open_sftp()

    # Delete images using SSH
    for image in annotations.image_path.unique():
        remote_path = os.path.join(folder_name, os.path.basename(image))
        # Archive annotations using SSH
        archive_annotation_path = os.path.join(folder_name, "archive")
        # sftp check if dir exists
        try:
            sftp.listdir(archive_annotation_path)
        except FileNotFoundError:
            raise FileNotFoundError("The archive directory {} does not exist.".format(archive_annotation_path))
        
        #Need sudo
        #sftp.rename(remote_path, os.path.join(archive_annotation_path, remote_path))
        print(f"Archived {image} successfully")

    ssh.close()
    


