import os
import cv2
from src.preprocessing import validate_image
from src.feature_extraction import get_strip_bbox, extract_features_from_strip
from src.color_matching import load_reference_dataset, predict_stage

def test_pipeline():
    base_dir = r"c:\Users\venka\Desktop\h2s\H2S-Dosimeter"
    
    # 1. Test Dataset exists
    csv_path = os.path.join(base_dir, "data", "processed", "h2s_dataset.csv")
    assert os.path.exists(csv_path), "Dataset CSV not found."
    df = load_reference_dataset(csv_path)
    assert not df.empty, "Dataset is empty."
    
    # 2. Test Image processing
    test_img_path = os.path.join(base_dir, "data", "cropped", "stage_04.jpg")
    assert os.path.exists(test_img_path), "Test image not found."
    
    with open(test_img_path, "rb") as f:
        img_bytes = f.read()
        
    is_valid, msg, img = validate_image(img_bytes)
    assert is_valid, f"Image validation failed: {msg}"
    
    # 3. Test Feature extraction
    strip_bbox = get_strip_bbox(img)
    features, roi_info, annotated_img = extract_features_from_strip(img, strip_bbox)
    assert "array_2_L" in features, "Failed to extract LAB features."
    assert "array_2_roi_pixels" in roi_info, "Failed to extract ROI info."
    assert annotated_img is not None, "Failed to generate annotated image"
    
    # 4. Test Prediction
    stage, dist, sim, ref, distances = predict_stage(features, df)
    assert stage == 4, f"Expected stage 4, got {stage}"
    assert len(distances) == len(df), "Did not calculate distances for all reference stages"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_pipeline()
