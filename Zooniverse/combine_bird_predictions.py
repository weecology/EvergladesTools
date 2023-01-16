import glob
import os
import re
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

import geopandas
import pandas as pd


def find_shp_files(predictions_path):
    files = glob.glob(os.path.join(predictions_path, '**', '**', '*_projected.shp'))
    return files


def get_site(path):
    path = os.path.basename(path)
    regex = re.compile("(\\w+)_\\d+_\\d+_\\d+.*_projected")
    return regex.match(path).group(1)


def get_date(path):
    path = os.path.basename(path)
    regex = re.compile('\\w+_(\\d+_\\d+_\\d+).*_projected')
    return regex.match(path).group(1)

def get_event(path):
    """
    Determines the event for a given UAS flight

    When there is only one event, the event is not typically recorded in the file name.
    So, values for path are of the general form:
    /path/to/file/site_month_day_year_projected.shp
    or
    /path/to/file/site_month_day_year_event_projected.shp

    This function returns "Primary" for no event and events with the following values:
    "A", "a", "primary", "PRIMARY", or mixed case versions of "primary"
    """
    path = os.path.basename(path)
    regex = re.compile('\\w+_\\d+_\\d+_\\d+_(\\w+)_projected')
    match = regex.match(path)
    if match and match.group(1).upper() != "A" and match.group(1).upper() != "PRIMARY":
        return match.group(1)
    else:
        return "Primary"

def load_shapefile(x):
    shp = geopandas.read_file(x)
    shp["site"] = get_site(x)
    shp["date"] = get_date(x)
    shp["event"] = get_event(x)
    return shp


def combine(paths, score_thresh):
    """Take prediction shapefiles and wrap into a single file"""
    shapefiles = []
    for x in paths:
        try:
            shapefiles.append(load_shapefile(x))
        except:
            print(f"Mistructured file path: {x}. File not added to PredictedBirds.shp")
    summary = geopandas.GeoDataFrame(pd.concat(shapefiles, ignore_index=True), crs=shapefiles[0].crs)
    summary = summary[summary.score > score_thresh]

    return summary


if __name__ == "__main__":
    score_thresh = 0.3
    predictions_path = "/blue/ewhite/everglades/predictions/"
    output_path = "/blue/ewhite/everglades/EvergladesTools/App/Zooniverse/data/"

    predictions = find_shp_files(predictions_path)
    # write output to zooniverse app
    df = combine(predictions, score_thresh)
    df.to_file(os.path.join(output_path, "PredictedBirds.shp"))

    # Zip the shapefile for storage efficiency
    with ZipFile("../App/Zooniverse/data/PredictedBirds.zip", 'w', ZIP_DEFLATED) as zip:
        for ext in ['cpg', 'dbf', 'prj', 'shp', 'shx']:
            focal_file = os.path.join(output_path, f"PredictedBirds.{ext}")
            file_name = os.path.basename(focal_file)
            zip.write(focal_file, arcname=file_name)
            os.remove(focal_file)
