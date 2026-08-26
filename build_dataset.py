import os
import cv2
import numpy as np
import pandas as pd

# Setup directories
base_dir = r"c:\Users\venka\Desktop\h2s\H2S-Dosimeter"
dirs = [
    "data/raw",
    "data/cropped",
    "data/processed",
    "src",
    "models",
    "mlops"
]

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

# Path to the raw image (Image 1 is the clean reference)
img_path = os.path.join(base_dir, "data", "raw", "image_1.jpg")
img = cv2.imread(img_path)

if img is None:
    print(f"Error: Could not read image at {img_path}")
    exit(1)

# Image shape is 558x1024
height, width = img.shape[:2]

rows = 3
cols = 12

strip_h = height // rows
strip_w = width // cols

# We will select 12 stages out of the 36 available to match the 12 provisional ppm values.
# Indices to select: 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33
selected_indices = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]

data = []

# Crop strips and extract features
for idx, flat_idx in enumerate(selected_indices):
    r = flat_idx // cols
    c = flat_idx % cols
    
    y1 = r * strip_h
    y2 = (r + 1) * strip_h
    x1 = c * strip_w
    x2 = (c + 1) * strip_w
    
    strip_img = img[y1:y2, x1:x2]
    
    # Save cropped strip
    stage_num = idx + 1
    crop_filename = f"stage_{stage_num:02d}.jpg"
    crop_filepath = os.path.join(base_dir, "data", "cropped", crop_filename)
    cv2.imwrite(crop_filepath, strip_img)
    
    # Each strip has 3 arrays (circles). Let's roughly crop them out.
    # The strip is roughly 186x85.
    # Array 1: top third, Array 2: middle third, Array 3: bottom third
    ah = strip_h // 3
    
    row_data = {
        "image_name": crop_filename,
        "stage": stage_num,
        "calibration_status": "IMAGE REFERENCE ONLY"
    }
    
    for array_idx in range(1, 4):
        ay1 = (array_idx - 1) * ah
        ay2 = array_idx * ah
        array_img = strip_img[ay1:ay2, :]
        
        # We need to extract the color from the circular region.
        # A simple way is to take the center pixels to avoid the white background.
        # Center bounding box:
        cy1 = int(ah * 0.35)
        cy2 = int(ah * 0.65)
        cx1 = int(strip_w * 0.35)
        cx2 = int(strip_w * 0.65)
        
        roi = array_img[cy1:cy2, cx1:cx2]
        
        # Calculate features
        mean_bgr = np.mean(roi, axis=(0, 1))
        std_bgr = np.std(roi, axis=(0, 1))
        
        # Convert to HSV
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mean_hsv = np.mean(roi_hsv, axis=(0, 1))
        
        # Convert to LAB
        roi_lab = cv2.cvtColor(roi, cv2.COLOR_BGR2Lab)
        mean_lab = np.mean(roi_lab, axis=(0, 1))
        std_lab = np.std(roi_lab, axis=(0, 1))
        
        prefix = f"array_{array_idx}_"
        
        row_data[f"{prefix}B"] = mean_bgr[0]
        row_data[f"{prefix}G"] = mean_bgr[1]
        row_data[f"{prefix}R"] = mean_bgr[2]
        
        row_data[f"{prefix}std_B"] = std_bgr[0]
        row_data[f"{prefix}std_G"] = std_bgr[1]
        row_data[f"{prefix}std_R"] = std_bgr[2]
        
        row_data[f"{prefix}H"] = mean_hsv[0]
        row_data[f"{prefix}S"] = mean_hsv[1]
        row_data[f"{prefix}V"] = mean_hsv[2]
        
        row_data[f"{prefix}L"] = mean_lab[0]
        row_data[f"{prefix}a"] = mean_lab[1]
        row_data[f"{prefix}b"] = mean_lab[2]
        
        row_data[f"{prefix}std_L"] = std_lab[0]
        row_data[f"{prefix}std_a"] = std_lab[1]
        row_data[f"{prefix}std_b"] = std_lab[2]
        
    data.append(row_data)

# Create DataFrame and save
df = pd.DataFrame(data)
csv_path = os.path.join(base_dir, "data", "processed", "h2s_dataset.csv")
df.to_csv(csv_path, index=False)
print(f"Dataset created successfully at {csv_path}")
