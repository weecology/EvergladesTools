# Predict module for labeling pipeline
from deepforest import main
import os
import svgwrite

def predict(image_path, save_dir, model_path):
    if model_path is None:
        m = main.deepforest()
        m.use_release()
    else:
        m = main.deepforest.load_from_checkpoint(model_path)
    boxes = m.predict_tile(image_path,patch_size=1500, patch_overlap=0.05)
    boxes = boxes[boxes["score"] > 0.3]
    basename = os.path.splitext(os.path.basename(image_path))[0]
    boxes.to_csv(os.path.join(save_dir, "{}.csv".format(basename)))

    #Write an svg to overlay in photoshop
    svg_path = os.path.join(save_dir, "{}.svg".format(basename))

    dwg = svgwrite.Drawing(svg_path, profile='tiny')

    # Create color ramp for each class in label_dict
    color_ramp = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999"]

    for index, box in boxes.iterrows():
        #get height and width 
        width = box["xmax"] - box["xmin"]
        height = box["ymax"] - box["ymin"]
        x, y, w, h = box["xmin"], box["ymin"], width, height
        # select color based on class
        boxes["label"] = boxes["label"].astype("category")
        color = color_ramp[boxes["label"].cat.codes[index]]
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), fill='none', stroke=color, stroke_width=2))  
    dwg.save()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Predict bounding boxes on an image')
    parser.add_argument('--image_path', type=str, help='Path to image')
    parser.add_argument('--save_dir', type=str, help='Directory to save csv and svg files')
    parser.add_argument('--model_path', type=str, help='Path to model checkpoint')
    args = parser.parse_args()
    predict(args.image_path, args.save_dir, args.model_path)