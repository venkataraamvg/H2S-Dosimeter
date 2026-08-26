import streamlit as st
import os
import cv2
import pandas as pd
from PIL import Image
import numpy as np

from src.preprocessing import validate_image, normalize_color
from src.feature_extraction import get_strip_bbox, extract_features_from_strip
from src.color_matching import load_reference_dataset, predict_stage
from src.config import PROVISIONAL_CALIBRATION, PPM_TO_MGM3, get_exposure_category, DISCLAIMER

st.set_page_config(page_title="H2S Exposure Analyzer", layout="centered")

st.markdown("================================================")
st.markdown("<h2 style='text-align: center;'>H₂S EXPOSURE ANALYZER</h2>", unsafe_allow_html=True)
st.markdown("================================================")

# Load Reference Dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, "data", "processed", "h2s_dataset.csv")

if not os.path.exists(dataset_path):
    st.error("Reference dataset not found. Please run build_dataset.py first.")
    st.stop()

reference_df = load_reference_dataset(dataset_path)

st.write("### Upload Strip Image")
uploaded_file = st.file_uploader("Choose Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image bytes
    bytes_data = uploaded_file.getvalue()
    
    # 1. Validation
    is_valid, msg, img = validate_image(bytes_data)
    
    if not is_valid:
        st.error(msg)
    else:
        st.markdown("------------------------------------------------")
        st.write("### ORIGINAL IMAGE")
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)
        
        # 2. ROI Extraction & Normalization
        # Using a fixed central proportion ROI for the prototype (documented limitation).
        strip_bbox = get_strip_bbox(img)
        
        # 3. Feature Extraction & Annotations
        features, roi_info, annotated_img = extract_features_from_strip(img, strip_bbox)
        
        st.markdown("------------------------------------------------")
        st.write("### DETECTED SENSING REGION (ROI)")
        st.write("Blue rectangle: Detected Strip Bounds. Green rectangles: Analyzed Sensing Regions (Arrays 1-3).")
        st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), use_container_width=True)
        
        if not features:
            st.error("Could not detect arrays in the sensing region.")
        else:
            # 4. Color Matching & Prediction
            stage, dist, sim, ref_row, all_distances = predict_stage(features, reference_df)
            
            st.markdown("------------------------------------------------")
            st.write("### ANALYSIS DETAILS")
            
            # Step 1: Image Dimensions
            st.write(f"**1. Uploaded Image Dimensions:** {img.shape[1]}x{img.shape[0]} pixels (WxH)")
            
            # Step 2: ROI Coordinates
            coords = roi_info['array_2_roi_coords']
            st.write(f"**2. Detected ROI Coordinates (Array 2):** X: {coords[0]} to {coords[2]}, Y: {coords[1]} to {coords[3]}")
            
            # Step 3: ROI Preview
            st.write("**3. ROI Preview (Array 2 Pixels Actually Analyzed):**")
            st.image(cv2.cvtColor(roi_info['array_2_roi_img'], cv2.COLOR_BGR2RGB), width=50)
            
            # Step 4: Number of pixels
            st.write(f"**4. Number of pixels analyzed:** {roi_info['array_2_roi_pixels']} pixels")
            
            # Step 5-7: Color Values
            st.write("#### Extracted Color Statistics (Array 2)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**5. RGB**")
                st.write(f"R: Mean = {features['array_2_R']:.2f}, Std = {features['array_2_std_R']:.2f}")
                st.write(f"G: Mean = {features['array_2_G']:.2f}, Std = {features['array_2_std_G']:.2f}")
                st.write(f"B: Mean = {features['array_2_B']:.2f}, Std = {features['array_2_std_B']:.2f}")
            with col2:
                st.write("**6. HSV**")
                st.write(f"H: Mean = {features['array_2_H']:.2f}, Std = {features['array_2_std_H']:.2f}")
                st.write(f"S: Mean = {features['array_2_S']:.2f}, Std = {features['array_2_std_S']:.2f}")
                st.write(f"V: Mean = {features['array_2_V']:.2f}, Std = {features['array_2_std_V']:.2f}")
            with col3:
                st.write("**7. CIELAB**")
                st.write(f"L*: Mean = {features['array_2_L']:.2f}, Std = {features['array_2_std_L']:.2f}")
                st.write(f"a*: Mean = {features['array_2_a']:.2f}, Std = {features['array_2_std_a']:.2f}")
                st.write(f"b*: Mean = {features['array_2_b']:.2f}, Std = {features['array_2_std_b']:.2f}")
                
            # Step 8 & 9: Reference stages and ΔE values
            st.write("#### 8 & 9. Reference Stages and ΔE Values")
            st.write("Comparing uploaded Array 2 mean LAB against all known reference stages (CIELAB ΔE76).")
            
            # Create a dataframe for neat display
            dist_data = []
            for ref_stage, ref_dist in sorted(all_distances.items()):
                dist_data.append({"Stage": int(ref_stage), "ΔE": round(ref_dist, 2)})
            st.dataframe(pd.DataFrame(dist_data).set_index("Stage").T)
            
            # Step 10 & 11: Closest Stage & Explanation
            st.write(f"**10. Closest Reference Stage:** Stage {int(stage)}")
            
            explanation = f"""
            **11. Explanation of Selection:** 
            The system extracted the actual pixels from the uploaded image's central Array 2 ROI. 
            The mean LAB color of the uploaded ROI is [L*={features['array_2_L']:.2f}, a*={features['array_2_a']:.2f}, b*={features['array_2_b']:.2f}].
            It calculated the CIELAB Euclidean distance (ΔE76) between this uploaded color and every known reference stage in the dataset.
            The minimum distance was {dist:.2f} for Stage {int(stage)}, so Stage {int(stage)} was selected as the closest match.
            """
            st.info(explanation)
            
            # Step 12: Mapping used
            st.write("**12. Mapping used for Provisional Result:**")
            st.write("Image Upload -> Fixed central bounding box -> Array ROI pixel extraction -> LAB conversion -> Mean color calculation -> ΔE matching against reference CSV -> Minimum ΔE Stage -> Lookup Provisional ppm from config")
            
            ppm_val = PROVISIONAL_CALIBRATION.get(int(stage), None)
            
            if ppm_val is not None:
                st.write(f"Lookup: Stage {int(stage)} -> mapped to **{ppm_val} ppm** in `src/config.py`.")
            else:
                st.write(f"Lookup: Stage {int(stage)} -> No provisional ppm mapped.")
                
            # Show the matched reference crop
            ref_img_path = os.path.join(base_dir, "data", "cropped", ref_row['image_name'])
            if os.path.exists(ref_img_path):
                ref_img = cv2.imread(ref_img_path)
                st.write("*Reference Stage Crop (for visual confirmation of color match):*")
                st.image(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB), width=50)
            
            st.markdown("------------------------------------------------")
            st.write("### PROVISIONAL RESULT")
            
            if ppm_val is not None:
                mgm3_val = ppm_val * PPM_TO_MGM3
                cat = get_exposure_category(ppm_val)
                
                st.write(f"**H₂S:** {ppm_val} ppm")
                st.write(f"**Equivalent:** {mgm3_val:.2f} mg/m³")
                st.write(f"**Exposure Category:** {cat}")
            else:
                st.write(f"**H₂S:** PROVISIONAL MAPPING NOT DEFINED FOR STAGE {int(stage)}")
                
            st.markdown("------------------------------------------------")
            st.write("### CALIBRATION STATUS:")
            st.error("PROVISIONAL - NOT LAB CALIBRATED")
            st.warning(DISCLAIMER)
