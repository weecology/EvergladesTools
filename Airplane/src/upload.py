import paramiko
import requests
import paramiko
import requests
import os
import subprocess

def upload_images(images, user, host, folder_name):
    # SCP file transfer
    for image in images:
        local_path = os.path.basename(image)
        subprocess.run(["scp", image, "{}@{}:{}}".format(user,host,folder_name)])
        print(f"Uploaded {image} successfully")


