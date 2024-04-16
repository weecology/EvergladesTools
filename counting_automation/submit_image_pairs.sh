# Run the pipeline
python scripts/create_image_pairs_for_annotation.py \
    --img_left /Users/benweinstein/Downloads/DSC_2520.JPG
    --img_right /Users/benweinstein/Downloads/DSC_2522.JPG \
    --model_path /blue/ewhite/everglades/Zooniverse/20220910_182547/species_model.pl \
    --user ben \
    --host serenity.ifas.ufl.edu \
    --key_filename /home/b.weinstein/.ssh/id_rsa.pub \
    --label_studio_url https://labelstudio.naturecast.org/ \
    --label_studio_project "Airplane Colony" \
    --label_studio_folder '/pgsql/retrieverdash/everglades-label-studio/everglades-data' \
