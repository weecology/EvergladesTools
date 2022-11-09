import glob
import os
import subprocess

import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling

import start_cluster 

subprocess.call("/orange/ewhite/everglades/mapbox/source_token.txt", shell =True)

def upload(path):
     try:
          #create output filename
          basename = os.path.splitext(os.path.basename(path))[0]
          mbtiles_filename = "/blue/ewhite/everglades/mapbox/{}.mbtiles".format(basename)
          
          dst_crs = rio.crs.CRS.from_epsg("3857")
     
          with rio.open(path) as src:
               transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
               kwargs = src.meta.copy()
               kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
               })
     
               #create output filename
               out_filename = "{}_projected.tif".format(os.path.splitext(path)[0])
     
               if not os.path.exists(out_filename):
                    with rio.open(out_filename, 'w', **kwargs) as dst:
                         for i in range(1, src.count + 1):
                              reproject(
                                   source=rio.band(src, i),
                               destination=rio.band(dst, i),
                               src_transform=src.transform,
                               src_crs=src.crs,
                               dst_transform=transform,
                               dst_crs=dst_crs,
                               resampling=Resampling.nearest)
     
          ## Create the mbtiles files
          if not os.path.exists(mbtiles_filename):
               subprocess.run(["touch", mbtiles_filename]) #The rio mbtiles command apparently requires that the output file already exist
               subprocess.run(["rio", "mbtiles", out_filename, "-o", mbtiles_filename, "--zoom-levels", "17..24", "-j", "4", "-f", "PNG"])

          ## Upload to mapbox
          subprocess.run(["mapbox", "upload", f"bweinstein.{basename}", mbtiles_filename])
     
     except Exception as e:
          return "path: {} raised: {}".format(path, e)
          
     return mbtiles_filename

if __name__=="__main__":
     
     files_to_upload = glob.glob("/blue/ewhite/everglades/orthomosaics/2022/**/*.tif", recursive=True)
     files_to_upload = [x for x in files_to_upload if "projected" not in x]
     
     for index, path in enumerate(files_to_upload):
          print(f"Uploading file {path} ({index + 1}/{len(files_to_upload)})")
          upload(path)
          
     client = start_cluster.start(cpus=20, mem_size="20GB")
     futures = client.map(upload,files_to_upload)
     
     completed_files = [x.result() for x in futures]
     print("Completed upload of {}".format(completed_files))
