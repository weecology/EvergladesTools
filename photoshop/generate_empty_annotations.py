import pandas as pd
import shapely
from deepforest.preprocess import split_raster
from deepforest import main
import os
import geopandas as gpd
import glob

def load(path):
    basename = os.path.splitext(os.path.basename(path))[0]        
    df = pd.read_csv(path)
    df["image_path"] = "{}.tif".format(basename)
    
    #Create geospatial frame
    df["x"] = df.Xpos.apply(lambda x: int(float(x.split(" ")[0])))
    df["y"] = df.Ypos.apply(lambda x: int(float(x.split(" ")[0])))
    df['geometry'] = df.apply(lambda x: shapely.geometry.Point(x.x,x.y), axis=1)
    df = gpd.GeoDataFrame(df, geometry='geometry')    
    
    return df
    
def lookup_raster(image_pool, basename):
    try:
        tifs = [x for x in image_pool if basename in x]
        tifs = [x for x in tifs if not "projected" in x]
        return tifs[0] 
    except:
        return None

def predict_boxes(image_path):
    m = main.deepforest()
    m.use_bird_release()    
    boxes = m.predict_tile(raster_path=image_path, patch_size=1500)
    boxes['geometry'] = boxes.apply(lambda x: shapely.geometry.box(x.xmin,x.ymin,x.xmax,x.ymax), axis=1)
    boxes = gpd.GeoDataFrame(boxes, geometry='geometry')    
        
    return boxes

def points_to_boxes(df, boxes):
    #Merge results with field data, buffer on edge 
    merged_boxes = gpd.sjoin(boxes, df, how="left")
    merged_boxes = merged_boxes.drop(columns=["xmin","xmax","ymin","ymax"])
    
    return merged_boxes    
    
def crop(annotations, image_path, base_dir):
    split_annotations = split_raster(annotations_file=annotations, path_to_raster=image_path, patch_size=1500, patch_overlap=0, base_dir=base_dir, allow_empty=True)
    
    return split_annotations

def run(paths, image_pool, base_dir):
    """For a given annotation file, predict bird detections, associate points with boxes and save a .csv for training"""
    
    crop_annotations = []
    for path in paths:
        print(path)
        df = load(path)
        basename = os.path.splitext(os.path.basename(path))[0] 
        image_path = lookup_raster(image_pool, basename)
        if image_path is None:
            continue
        boxes = predict_boxes(image_path)
        merged_boxes = points_to_boxes(df, boxes)
        
        #Format for deepforest image_path, xmin, ymin, xmax, ymax, label
        merged_boxes = pd.concat([merged_boxes,merged_boxes.bounds], 1).rename(columns={"minx": "xmin","miny":"ymin","maxx":"xmax","maxy":"ymax"})
        merged_boxes.to_csv("{}/raw_annotations_{}.csv".format(base_dir, basename))
        annotations = crop(annotations="{}/raw_annotations_{}.csv".format(base_dir, basename), image_path=image_path, base_dir=base_dir)
        print("There are {} annotations in the cropped csv".format(annotations.shape[0]))
        annotations.to_csv("{}/crop_annotations_{}.csv".format(base_dir, basename))
        crop_annotations.append(annotations)
    
    crop_annotations = pd.concat(crop_annotations)
    images_to_keep = crop_annotations[crop_annotations.Species.isnull()].image_path.unique()
    has_true_positive = crop_annotations[~crop_annotations.Species.isnull()].image_path.unique()
    images_to_keep = [x for x in images_to_keep if x not in has_true_positive]
    crop_annotations = crop_annotations[crop_annotations.image_path.isin(images_to_keep)]
    crop_annotations.to_csv("{}/inferred_empty_annotations.csv".format(base_dir))
    
    return crop_annotations

if __name__ == "__main__":    
    paths = glob.glob("/home/b.weinstein/EvergladesTools/photoshop/csvs/*")
    image_pool = glob.glob("/blue/ewhite/everglades/orthomosaics/**/**/*", recursive=True)
    base_dir = "/blue/ewhite/everglades/photoshop_annotations/"
    
    run(paths, image_pool, base_dir)    