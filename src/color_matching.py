import numpy as np
import pandas as pd
import math

def load_reference_dataset(csv_path):
    return pd.read_csv(csv_path)

def color_distance_cielab(lab1, lab2):
    """
    Calculate Euclidean distance in CIELAB color space (Delta E 76).
    """
    dl = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return math.sqrt(dl**2 + da**2 + db**2)

def predict_stage(features, reference_df):
    """
    Predict reaction stage using nearest-reference color matching.
    Returns:
    - best_stage: The closest matching stage number
    - min_dist: The minimum Delta E
    - similarity: A percentage similarity score
    - best_ref: The reference row that matched
    - distances: A dictionary of all stage distances
    """
    best_stage = None
    min_dist = float('inf')
    best_ref = None
    
    distances = {}
    
    # We will use Array 2 as the primary indicator for this simple prototype
    # Future versions will use Array 1 + Array 2 + Array 3
    query_lab = (features['array_2_L'], features['array_2_a'], features['array_2_b'])
    
    for _, row in reference_df.iterrows():
        ref_lab = (row['array_2_L'], row['array_2_a'], row['array_2_b'])
        dist = color_distance_cielab(query_lab, ref_lab)
        
        stage = row['stage']
        distances[stage] = dist
        
        if dist < min_dist:
            min_dist = dist
            best_stage = stage
            best_ref = row
            
    # Calculate a simple similarity score (0-100%)
    max_practical_dist = 100.0 
    similarity = max(0, 100 - (min_dist / max_practical_dist * 100))
            
    return best_stage, min_dist, similarity, best_ref, distances
