Zenodo README

The following training and test data are provided to support everglades wading bird species detection models. For modeling results and architectures see (cometML experiment)[https://www.comet.com/bw4sz/everglades-species/100d0361daaf4f008380ede071deeb4a?experiment-tab=code]. 

# Dataset contents

* There are 313 images in test.csv file. 
* There are 2742 images in train file.

# Dataset structure

All images are in the zenodo_upload.zip folder. Raw annotations are in the shapefiles with the same corresponding basename as the images. The annotations have been collected into a pandas dataframe for training and test with the following columns.

* xmin, xmax, ymin, ymax - coordinates for the ground truth bounding box
* image_path - basename of the image
* label - Species label
