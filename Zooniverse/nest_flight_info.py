import json
import os
import sys
import time

def update_nest_flights_info(basename, savedir):
    """Update the nest_flights_info file to indicate that file has been processed
    
    This is import for the snakemake pipeline and also provides metadata
    on when a given ortho was last processed.
    """
    if os.path.exists(f"{savedir}/nest_flights_info.json"):
        json_file = open(f"{savedir}/nest_flights_info.json", "r")
        nest_flights_info = json.load(json_file)
        json_file.close()
    else:
        nest_flights_info = {}
    nest_flights_info[basename] = time.asctime(time.localtime(time.time()))
    with open(f"{savedir}/nest_flights_info.json", "w") as json_file:
        json.dump(nest_flights_info, json_file, indent=2)

if __name__ == "__main__":
    paths = sys.argv[1:]
    split_path = os.path.normpath(paths[0]).split(os.path.sep)
    ###
    year = split_path[9]
    site = split_path[10]

    savedir = os.path.join("/home/ethan/Dropbox/Research/Everglades/EvergladesTools/Zooniverse/predictions/", year, site)
    # result = run(proj_tile_path=path, checkpoint_path=checkpoint_path, savedir=savedir)
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    for path in paths:
        basename = os.path.splitext(os.path.basename(path))[0]
        update_nest_flights_info(basename, savedir)