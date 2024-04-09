# Use rclone to look for images in dropbox
rclone move UFdropbox:/Airplane_images_to_predict/* UFdropbox:/Airplane_images_to_predict/processed
rclone copy /blue/ewhite/everglades/Airplane/annotations UFdropbox:/Airplane_images_to_predict/processed