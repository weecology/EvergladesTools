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
    df["x"] = df.Xpos.apply(lambda x: int(x.split(" ")[0]))
    df["y"] = df.Ypos.apply(lambda x: int(x.split(" ")[0]))
    df['geometry'] = df.apply(lambda x: shapely.geometry.Point(x.x,x.y), axis=1)
    df = gpd.GeoDataFrame(df, geometry='geometry')    
    
    return df
    
def lookup_raster(image_pool, basename):
    try:
        return [x for x in image_pool if basename in x][0] 
    except:
        return None

def predict_boxes(image_path):
    m = main.deepforest()
    m.use_bird_release()    
    boxes = m.predict_tile(raster_path=image_path, patch_size=1500)
    boxes['geometry'] = boxes.apply(lambda x: shapely.geometry.box(x.xmin,x.ymin,x.xmax,x.ymax), axis=1)
    boxes = gpd.GeoDataFrame(boxes, geometry='geometry')    
        
    return boxes

def create_boxes(df, size=30):
    """If there are no deepforest boxes, fall back on selecting a fixed area around stem point"""
    fixed_boxes = df.buffer(size).envelope
    
    fixed_boxes = gpd.GeoDataFrame(geometry=fixed_boxes)
    
    #Mimic the existing structure
    fixed_boxes = gpd.sjoin(fixed_boxes, df)
    fixed_boxes["score"] = None
    fixed_boxes["label"] = "Tree" 
    fixed_boxes["xmin"] = None 
    fixed_boxes["xmax"] = None
    fixed_boxes["ymax"] = None
    fixed_boxes["ymin"] = None
    
    fixed_boxes["box_id"] = fixed_boxes.index.to_series().apply(lambda x: "fixed_box_{}".format(x))
    
    return fixed_boxes


def choose_box(group, df):
    """Given a set of overlapping bounding boxes and predictions, just choose the closest to stem box by centroid if there are multiples"""
    if group.shape[0] == 1:
        return  group
    else:
        #Find centroid
        individual_id = group.individual.unique()[0]
        stem_location = df[df["individual"]==individual_id].geometry.iloc[0]
        closest_stem = group.centroid.distance(stem_location).sort_values().index[0]
        
        return group.loc[[closest_stem]]

def points_to_boxes(df, boxes):
    #Merge results with field data, buffer on edge 
    merged_boxes = gpd.sjoin(boxes, df)

    ##If no remaining boxes just take a box around center
    missing_ids = df[~df.ItemNumber.isin(merged_boxes.ItemNumber)]

    if not missing_ids.empty:
        created_boxes = create_boxes(missing_ids)
        merged_boxes = merged_boxes.append(created_boxes)

    #If there are multiple boxes per point, take the center box
    grouped = merged_boxes.groupby("ItemNumber")

    cleaned_boxes = []
    for value, group in grouped:
        choosen_box = choose_box(group, df)
        cleaned_boxes.append(choosen_box)

    merged_boxes = gpd.GeoDataFrame(pd.concat(cleaned_boxes),crs=merged_boxes.crs)
    merged_boxes = merged_boxes.drop(columns=["xmin","xmax","ymin","ymax"])
    
    return merged_boxes    
    
def crop(annotations, image_path, base_dir):
    split_annotations = split_raster(annotations_file=annotations, path_to_raster=image_path, patch_size=1500, patch_overlap=0, base_dir=base_dir)
    
    return split_annotations

def run(paths, image_pool, base_dir):
    """For a given annotation file, predict bird detections, associate points with boxes and save a .csv for training"""
    for path in paths:
        df = load(path)
        basename = os.path.splitext(os.path.basename(path))[0] 
        image_path = lookup_raster(image_pool, basename)
        if image_path is None:
            continue
        boxes = predict_boxes(image_path)
        merged_boxes = points_to_boxes(df, boxes)
        
        #Format for deepforest image_path, xmin, ymin, xmax, ymax, label
        merged_boxes = pd.concat([merged_boxes[["image_path","label"]],merged_boxes.bounds], 1).rename(columns={"minx": "xmin","miny":"ymin","maxx":"xmax","maxy":"ymax"})
        merged_boxes.to_csv("{}/raw_annotations.csv".format(base_dir))
        annotations = crop(annotations="{}/raw_annotations.csv".format(base_dir), image_path=image_path, base_dir=base_dir)
    annotations.to_csv("{}/split_annotations.csv".format(base_dir))
    
    return annotations

if __name__ == "__main__":    
    paths = glob.glob("/home/benweinstein/Documents/EvergladesTools/photoshop/csvs/*")
    image_pool = glob.glob("/blue/ewhite/everglades/orthomosaics/*", recursive=True)
    base_dir = "/blue/ewhite/everglades/photoshop_annotations/"
    
    run(paths, image_pool, base_dir)    