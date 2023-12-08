import paramiko
import requests
import os
import subprocess

def upload_images(images, user, host, folder_name):
    # SCP file transfer
    for image in images:
        local_path = os.path.basename(image)
        subprocess.run(["scp", image, "{}@{}:{}}".format(user, host, folder_name)])
        print(f"Uploaded {image} successfully")

def remove_annotated_image_remote_server(annotations, user, host, folder_name):
    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user)

    # Delete images using SSH
    for image in annotations:
        remote_path = os.path.join(folder_name, os.path.basename(image))
        command = "rm {}".format(remote_path)
        ssh.exec_command(command)
        print(f"Deleted {image} successfully")

    ssh.close()
    


