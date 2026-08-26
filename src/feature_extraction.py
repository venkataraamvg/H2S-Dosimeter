import cv2
import numpy as np

def get_strip_bbox(img):
    """
    Returns the bounding box (x1, y1, x2, y2) of the strip within the original image.
    Currently uses a fixed central crop for wide images, or the whole image.
    """
    h, w = img.shape[:2]
    if w > h:
        # Expected ratio of strip is roughly 186:85 ~ 2.18 (h/w)
        target_w = int(h / 2.18)
        start_x = (w - target_w) // 2
        return start_x, 0, start_x + target_w, h
    return 0, 0, w, h

def extract_features_from_strip(img):
    """
    Extracts color features from the original image using fractional coordinates
    that match the frontend UI overlay perfectly.
    """
    h, w = img.shape[:2]
    
    features = {}
    roi_info = {}
    
    # Annotated image (copy of original)
    annotated_img = img.copy()
    
    # Coordinates matching frontend REGIONS exactly
    regions = {
        1: {'x': 0.27, 'y': 0.15, 'w': 0.22, 'h': 0.14}, # fast
        2: {'x': 0.27, 'y': 0.43, 'w': 0.22, 'h': 0.14}, # medium
        3: {'x': 0.27, 'y': 0.71, 'w': 0.22, 'h': 0.14}, # slow
    }
    
    for array_idx, r in regions.items():
        abs_x1 = int(r['x'] * w)
        abs_y1 = int(r['y'] * h)
        abs_x2 = int((r['x'] + r['w']) * w)
        abs_y2 = int((r['y'] + r['h']) * h)
        
        roi = img[abs_y1:abs_y2, abs_x1:abs_x2]
        
        if roi.size == 0:
            continue
            
        roi_info[f"array_{array_idx}_roi_coords"] = (abs_x1, abs_y1, abs_x2, abs_y2)
        roi_info[f"array_{array_idx}_roi_pixels"] = roi.shape[0] * roi.shape[1]
        roi_info[f"array_{array_idx}_roi_img"] = roi
        
        # Draw ROI boundary in green
        cv2.rectangle(annotated_img, (abs_x1, abs_y1), (abs_x2, abs_y2), (0, 255, 0), 2)
            
        mean_bgr = np.mean(roi, axis=(0, 1))
        std_bgr = np.std(roi, axis=(0, 1))
        
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mean_hsv = np.mean(roi_hsv, axis=(0, 1))
        std_hsv = np.std(roi_hsv, axis=(0, 1))
        
        roi_lab = cv2.cvtColor(roi, cv2.COLOR_BGR2Lab)
        mean_lab = np.mean(roi_lab, axis=(0, 1))
        std_lab = np.std(roi_lab, axis=(0, 1))
        
        prefix = f"array_{array_idx}_"
        
        features[f"{prefix}B"] = mean_bgr[0]
        features[f"{prefix}G"] = mean_bgr[1]
        features[f"{prefix}R"] = mean_bgr[2]
        features[f"{prefix}std_B"] = std_bgr[0]
        features[f"{prefix}std_G"] = std_bgr[1]
        features[f"{prefix}std_R"] = std_bgr[2]
        
        features[f"{prefix}H"] = mean_hsv[0]
        features[f"{prefix}S"] = mean_hsv[1]
        features[f"{prefix}V"] = mean_hsv[2]
        features[f"{prefix}std_H"] = std_hsv[0]
        features[f"{prefix}std_S"] = std_hsv[1]
        features[f"{prefix}std_V"] = std_hsv[2]
        
        features[f"{prefix}L"] = mean_lab[0]
        features[f"{prefix}a"] = mean_lab[1]
        features[f"{prefix}b"] = mean_lab[2]
        features[f"{prefix}std_L"] = std_lab[0]
        features[f"{prefix}std_a"] = std_lab[1]
        features[f"{prefix}std_b"] = std_lab[2]
        
    return features, roi_info, annotated_img
