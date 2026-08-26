import os
import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify, render_template

from src.preprocessing import validate_image, normalize_color
from src.feature_extraction import get_strip_bbox, extract_features_from_strip
from src.color_matching import load_reference_dataset, predict_stage
from src.config import PROVISIONAL_CALIBRATION, PPM_TO_MGM3, get_exposure_category

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, "data", "processed", "h2s_dataset.csv")
reference_df = load_reference_dataset(dataset_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sample')
def sample():
    import random
    stage_num = random.randint(1, 12)
    img_path = os.path.join(base_dir, "data", "cropped", f"stage_{stage_num:02d}.jpg")
    
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    
    return jsonify({
        "image": "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode('utf-8')
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400
        
    img_data = data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_data)
    
    is_valid, msg, img = validate_image(img_bytes)
    if not is_valid:
        return jsonify({'error': msg}), 400
        
    features, roi_info, _ = extract_features_from_strip(img)
    
    if not features:
        return jsonify({'error': 'Could not detect arrays in the sensing region.'}), 400
        
    stage, dist, sim, ref_row, all_distances = predict_stage(features, reference_df)
    
    ppm_val = PROVISIONAL_CALIBRATION.get(int(stage), 0.0)
    cat = get_exposure_category(ppm_val).upper()
    
    # We map the backend features to the frontend format
    response = {
        'colours': {
            'fast': [features['array_1_R'], features['array_1_G'], features['array_1_B']],
            'medium': [features['array_2_R'], features['array_2_G'], features['array_2_B']],
            'slow': [features['array_3_R'], features['array_3_G'], features['array_3_B']],
            'ref': [201, 201, 201] # Dummy ref
        },
        'exposureResult': {
            'exposure': float(ppm_val),
            'riskLevel': cat,
            'deltaEs': {
                'fast': float(dist), # Simplified for frontend UI tracking
                'medium': float(dist), 
                'slow': float(dist)
            }
        },
        'backend_info': {
            'stage': int(stage),
            'similarity': float(sim),
            'min_dist': float(dist)
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
