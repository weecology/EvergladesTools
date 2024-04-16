# Create label-studio json for pair on images right img-left, img-right tags
from scripts.labelstudio import upload_paired_images
import argparse

parser = argparse.ArgumentParser(description='Create image pairs for annotation')
parser.add_argument('--img_left', type=str, help='Path to left image')
parser.add_argument('--img_right', type=str, help='Path to right image')
parser.add_argument('--user', type=str, help='SFTP username')
parser.add_argument('--folder', type=str, help='SFTP folder')
parser.add_argument('--host', type=str, help='SFTP host')
parser.add_argument('--key_filename', type=str, help='Path to private key')
parser.add_argument('--label_studio_url', type=str, help='Label Studio URL')
parser.add_argument('--label_studio_project', type=str, help='Label Studio project name')
parser.add_argument('--model_path', type=str, help='Path to model checkpoint')
args = parser.parse_args()

upload_paired_images([args.img_left, args.img_right], args.user, args.folder, args.host, args.key_filename, args.label_studio_url, args.label_studio_project)

