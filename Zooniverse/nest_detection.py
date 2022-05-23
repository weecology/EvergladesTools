#Bird Bird Bird Detector
# Given a set of predictions in /orange/ewhite/everglades/predictions/, generate predicted nests
import glob
import geopandas
import sys
import rtree
import rasterio
import random
import os
import pandas as pd
import cv2
import numpy as np
from panoptes_client import Panoptes, Project, SubjectSet, Subject
import utils
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from pathlib import Path

from rasterio.windows import from_bounds
from PIL import Image, ImageDraw

def get_date(x):
    """parse filename to return event name"""
    basename = os.path.basename(x)
    event = basename.split("_")[1:4]
    event = "_".join(event)
    
    return event

def load_files(dirname):
    """Load shapefiles and concat into large frame"""
    shapefiles = glob.glob(dirname + "*.shp")
    shapefiles = [x for x in shapefiles if "projected" in x]
    
    #load all shapefiles to create a dataframe
    df = []
    for x in shapefiles:
        try:
        # Catch and skip badly structured file names
        # TODO: fix file naming issues so we don't need this
            print(x)
            eventdf = geopandas.read_file(x)
            eventdf["Date"] = get_date(x)
            df.append(eventdf)
        except IndexError as e:
            print("Filename issue:")
            print(e)
    df = geopandas.GeoDataFrame(pd.concat(df, ignore_index=True))
    df.crs = eventdf.crs
    
    return df

def calculate_IoUs(geom, match):
    """Calculate intersection-over-union scores for a pair of boxes"""
    intersection = geom.intersection(match).area
    union = geom.union(match).area
    iou = intersection/float(union)
    
    return iou

def detect_nests(gdf):
    """Iterate over a dataframe and check rows"""
    results = []
    claimed_indices = []
    
    #Create spatial index
    spatial_index = gdf.sindex
    
    for index, row in gdf.iterrows():
        #skip is already claimed
        if index in claimed_indices:
            continue
            
        claimed_indices.append(index)
        geom = row["geometry"]
        
        #Look up matches
        possible_matches_index = list(spatial_index.intersection(geom.bounds))
        possible_matches = gdf.iloc[possible_matches_index]

        #Remove matches to the current date, which are nearby birds not the same bird on a different date
        possible_matches = possible_matches.loc[possible_matches['Date'] != row.Date]

        #Check for multiple matches from the same date and pick best match
        match_date_count = possible_matches.groupby('Date').Date.agg('count')
        multiple_match_dates = match_date_count[match_date_count > 1]

        if not multiple_match_dates.empty:
            for date in multiple_match_dates.index:
                multiple_matches = possible_matches[possible_matches['Date'] == date]
                multiple_matches = multiple_matches.assign(iou=multiple_matches['geometry'].map(lambda x: calculate_IoUs(x, geom)))
                best_match = multiple_matches[multiple_matches["iou"] == max(multiple_matches['iou'])].drop('iou', axis=1)
                possible_matches = possible_matches.drop(possible_matches[possible_matches['Date'] == date].index)
                possible_matches = possible_matches.append(best_match)

        #Remove any matches that are claimed by another nest detection
        matches = possible_matches[~(possible_matches.index.isin(claimed_indices))]
        
        if matches.empty:
            continue
        
        #add to claimed
        claimed_indices.extend(matches.index.values)
        
        #add target info to match
        matches = matches.append(row)
        matches["target_index"] = index
        matches = matches.rename(columns={"xmin":"matched_xmin","xmax":"matched_xmax","ymin":"matched_ymin","ymax":"matched_ymax"})

        results.append(matches)
    
    if len(results) == 0:
        return None
        
    results = pd.concat(results)
    results = results.reset_index(drop=True)
    
    return results
        
def check_overlap(geom, gdf):
    """Find spatially overlapping rows between target and pool of geometries"""
    matches = gdf.intersects(geom)
    
    return matches


def count_max_consec_detects(nest_data, date_data):
    """Determine the maximum number of consecutive bird detections"""
    assert date_data.shape[0] == 1, "date_data should be a Pandas DataFrame with one row"
    sorted_dates = pd.Series(date_data.Date[0]).sort_values().reset_index(drop=True)
    sorted_nest_dates = pd.Series(nest_data.Date).sort_values().reset_index(drop=True)
    sorted_dates_dict = {val: key for key, val in sorted_dates.items()}
    sorted_dates_combined_diff = sorted_nest_dates.map(sorted_dates_dict).diff()
    all_consec_detects = []
    consec_detects = 0
    for i in range(1, len(sorted_dates_combined_diff)):
        if sorted_dates_combined_diff[i] == 1 and sorted_dates_combined_diff[i-1] != 1:
            # New start to consectutive detection set
            consec_detects = 1
            if i + 1 == len(sorted_dates_combined_diff):
                all_consec_detects.append(consec_detects)
        elif sorted_dates_combined_diff[i] == 1 and sorted_dates_combined_diff[i-1] == 1:
            # Increment existing consecutive detection set
            consec_detects += 1
            if i + 1 == len(sorted_dates_combined_diff):
                all_consec_detects.append(consec_detects)
        elif sorted_dates_combined_diff[i] != 1 and sorted_dates_combined_diff[i-1] == 1:
            # Store completed consecutive detection set and reset
            all_consec_detects.append(consec_detects)
            consec_detects = 0
        elif sorted_dates_combined_diff[i] != 1 and sorted_dates_combined_diff[i-1] != 1:
            consec_detects == 0
        else:
            assert False, "Oops, I shouldn't be here"
    if all_consec_detects:
        max_consec_detects = max(all_consec_detects)
    else:
        max_consec_detects = 0

    return max_consec_detects

def process_nests(nests_data, savedir, min_score=0.3, min_detections=3, min_consec_detects = 1):
    """Process nests into a one row per nest table"""
    dates_data = nests_data.groupby(['Site', 'Year']).agg({'Date': lambda x: x.unique().tolist()}).reset_index()
    target_inds = nests_data['target_index'].unique()
    nests = []
    for target_ind in target_inds:
        nest_data = nests_data[(nests_data['target_index'] == target_ind) & (nests_data['score'] >= min_score)]
        date_data = dates_data[(dates_data['Site'] == nests_data['Site'][0]) & (dates_data['Year'] == nests_data['Year'][0])]
        num_consec_detects = count_max_consec_detects(nest_data, date_data)
        if len(nest_data) >= min_detections or num_consec_detects >= min_consec_detects:
            summed_scores = nest_data.groupby(['Site', 'Year', 'target_index', 'label']).score.agg(['sum', 'count'])
            top_score_data = summed_scores[summed_scores['sum'] == max(summed_scores['sum'])].reset_index()
            nest_info = nest_data.groupby(['Site', 'Year', 'target_index']).agg({'Date': ['min', 'max', 'count'], 
                                                                            'matched_xmin': ['mean'],
                                                                            'matched_ymin': ['mean'],
                                                                            'matched_xmax': ['mean'],
                                                                            'matched_ymax': ['mean']}).reset_index()
            xmean = (nest_info['matched_xmin']['mean'][0] + nest_info['matched_xmax']['mean']) / 2
            ymean = (nest_info['matched_ymin']['mean'][0] + nest_info['matched_ymax']['mean']) / 2
            nests.append([target_ind,
                        nest_info['Site'][0],
                        nest_info['Year'][0],
                        xmean[0],
                        ymean[0],
                        nest_info['Date']['min'][0],
                        nest_info['Date']['max'][0],
                        nest_info['Date']['count'][0],
                        top_score_data['label'][0],
                        top_score_data['sum'][0],
                        top_score_data['count'][0]])

    nests = pd.DataFrame(nests, columns=['nest_id', 'Site', 'Year', 'xmean', 'ymean',
                                'first_obs', 'last_obs', 'num_obs',
                                'species', 'sum_top1_score', 'num_obs_top1'])
    nests_shp = geopandas.GeoDataFrame(nests,
                                       geometry=geopandas.points_from_xy(nests.xmean, nests.ymean))
    nests_shp.crs = nests_data.crs
    save_path = f"{savedir}/nest_detections.shp"
    nests_shp.to_file(save_path)
    
    return(save_path)

def find_rgb_paths(site, paths):
    paths = [x for x in paths if site in x]
    paths.sort()
    
    return paths

def crop(rgb_path, geom, extend_box=3):
    src = rasterio.open(rgb_path)
    left, bottom, right, top = geom.bounds    
    window = from_bounds(left - extend_box,
                             bottom - extend_box,
                             right + extend_box,
                             top + extend_box,
                             transform=src.transform)
    
    numpy_array = src.read(window=window)
    numpy_array_rgb = np.rollaxis(numpy_array, 0,3)    
    numpy_array_bgr = numpy_array_rgb[:,:,::-1]   
    
    return numpy_array_bgr
    
def crop_images(df, rgb_images):
    """Crop images for a series of data"""
    crops = {}
    geom = df.geometry.iloc[0]
    target_ind = df.target_ind.unique()[0]
   
    for tile in rgb_images:
        #find rgb data
        basename = os.path.splitext(os.path.basename(tile))[0]
        datename = "{}_{}".format(target_ind, basename)
        crops[datename] = crop(tile, geom)
    
    return crops

def create_subject(filenames, everglades_watch):
    subject = Subject()

    subject.links.project = everglades_watch
    print("adding subjects: {}".format(filenames))
    for filename in filenames:
        subject.add_location(filename)
        subject.metadata.update({"filename":filename})

    #Trigger upload
    subject.save()    
    
    return subject
    
def create_subject_set(everglades_watch, name="Nest detections 2.0"):
    subject_set = SubjectSet()
    subject_set.links.project = everglades_watch
    subject_set.display_name = name
    subject_set.save()

    return subject_set

def write_timestamp(image, text):
    text = text.replace("_projected","")
    image = Image.fromarray(image)
    draw = ImageDraw.Draw(image)  
    draw.text((10, 10), text)  
    return np.array(image)
    
def extract_nests(filename, rgb_pool, savedir, upload=False):
    gdf = geopandas.read_file(filename)
    grouped = gdf.groupby("target_ind")
    if upload:
        everglades_watch = utils.connect()
        subject_set = create_subject_set(everglades_watch)
        subjects = []
    
    for name, group in grouped:
        #atleast three detections
        if group.shape[0] < 3:
            continue
        
        #Crop with date names as key
        site = group.Site.unique()[0]
        rgb_images = find_rgb_paths(site, rgb_pool)
        crops = crop_images(group, rgb_images=rgb_images)
        
        #save output
        dirname =  "{}/{}_{}".format(savedir,name,group["Site"].unique()[0])
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        
        filenames = []
        for datename in crops:
            filename = "{}/{}.png".format(dirname, datename)
            crop = crops[datename]
            if not crop.shape[2] == 3:
                print(f"[SKIP] Crop does not have three channels: {filename}")
                continue
            if (crop.shape[0] == 0) or (crop.shape[1] == 0):
                print(f"[SKIP] Crop overlaps edge of tile: {filename}")
                continue
            
            cv2.imwrite(filename, crop)
            filenames.append(filename)
            
        if upload:
            subject = create_subject(filenames, everglades_watch)
            subjects.append(subject)
            
    if upload:
        random.shuffle(subjects)
        subject_set.add(subjects)

if __name__=="__main__":
    #Write nests into folders of clips
    path = sys.argv[1]
    split_path = os.path.normpath(path).split(os.path.sep)
    year = split_path[5]
    site = split_path[6]
        
    #Load all shapefiles in this dir
    gdf = load_files("/blue/ewhite/everglades/predictions/{}/{}/".format(year, site))  
    nests_data = detect_nests(gdf)
    nests_data["Year"] = year
    nests_data["Site"] = site 
    
    print(nests_data.columns)
    
    processed_nests_path = process_nests(nests_data, savedir="/blue/ewhite/everglades/nests/{}/{}/".format(year, site))