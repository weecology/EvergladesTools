import easyidp as idp
print(idp.__version__)
ms = idp.Metashape("/Users/benweinstein/Dropbox/Weecology/everglades_species/easyidp/Hidden_Little_03_24_2022.psx", chunk_id=0)
roi = idp.ROI("/Users/benweinstein/Dropbox/Weecology/everglades_species/easyidp/example_bird.shp") 
img_dict = roi.back2raw(ms)



