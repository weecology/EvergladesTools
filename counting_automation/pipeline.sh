# A computer vision pipeline to look for images in a directory, submit prediction jobs, serve image results in label studio and generate reports/dashboards.

# Step 1: Look for images in a directory
bash scripts/look_for_images.sh

# Step 2: Submit prediction jobs
bash scripts/submit_prediction.sh

# Step 3: Reupload to dropbox
bash scripts/reupload_to_dropbox.sh
