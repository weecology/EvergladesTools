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


def download_annotations(user, host, folder_name, password, annotated_images_dir):
    """Download annotations from the Label Studio server.
    
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

    # Loop through downloaded JSON files and convert them to dataframes
    annotations = []
    for json_file in glob.glob(os.path.join(annotated_images_dir, "*.json")):
        annotations.append(data.convert_json_to_dataframe(json_file))
    annotations = pd.concat(annotations)

    return annotations

def remove_annotated_image_remote_server(annotations, user, host, folder_name, password):
    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # Delete images using SSH
    for image in annotations:
        remote_path = os.path.join(folder_name, os.path.basename(image))
        command = "rm {}".format(remote_path)
        ssh.exec_command(command)
        print(f"Deleted {image} successfully")

    ssh.close()
    


