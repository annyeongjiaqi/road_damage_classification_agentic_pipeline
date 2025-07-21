import os
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

# Config
source_dir = Path("raw_dataset")
target_dir = Path("dataset")
target_labels = ['D00', 'D10', 'D20', 'D40']
countries = ['India', 'Japan']

# Ensure target folders exist
for label in target_labels:
    (target_dir / label).mkdir(parents=True, exist_ok=True)

# Go through each country
for country in countries:
    ann_dir = source_dir / country / "train" / "annotations"
    img_dir = source_dir / country / "train" / "images"
    
    if not ann_dir.exists() or not img_dir.exists():
        print(f"Skipping {country} due to missing folders.")
        continue

    for ann_file in ann_dir.glob("*.xml"):
        tree = ET.parse(ann_file)
        root = tree.getroot()
        filename = root.find("filename").text
        labels_found = set()

        for obj in root.findall("object"):
            label = obj.find("name").text
            if label in target_labels:
                labels_found.add(label)

        for label in labels_found:
            src_img_path = img_dir / filename
            dest_path = target_dir / label / filename
            if src_img_path.exists():
                shutil.copy(src_img_path, dest_path)

print("Dataset organized using annotations into dataset/D00, D10, D20, D40")
