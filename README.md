# H₂S Exposure Dosimeter - Software Prototype

## 1. Project Overview
This project is a computer-vision proof-of-concept for a low-cost wearable passive H₂S (hydrogen sulfide) exposure dosimeter. The application analyzes a photograph of a Cu-PAN sensing strip, extracts color features, and matches them against a reference dataset to estimate the reaction stage.

## 2. Scientific Limitation
**CRITICAL:** This prototype uses provisional calibration labels for software demonstration ONLY. It is NOT a validated H₂S detector and must not be used for occupational safety decisions. The actual H₂S ppm values, exposure durations, and cumulative dose are NOT yet experimentally validated.

## 3. Installation
1. Ensure Python 3.8+ is installed.
2. Clone the repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Folder Structure
```
H2S-Dosimeter/
├── data/
│   ├── raw/          # Original uncropped images
│   ├── cropped/      # Cropped sensing strip images (Stages 1-12)
│   └── processed/    # Extracted color features dataset
├── src/
│   ├── config.py             # Provisional mappings and configuration
│   ├── preprocessing.py      # Image quality checks and ROI extraction
│   ├── feature_extraction.py # RGB, HSV, LAB extraction
│   └── color_matching.py     # Nearest-reference matching logic
├── mlops/            # Future ML pipeline and training scripts
├── app.py            # Streamlit web application
└── requirements.txt
```

## 5. Dataset Creation
To build the initial image reference dataset from a raw image containing the reference strips:
```bash
python build_dataset.py
```
This extracts the sensing strips, calculates color features (RGB, HSV, LAB) for each of the 3 arrays, and generates `data/processed/h2s_dataset.csv`.

## 6. How Image Processing Works
1. **Validation:** Checks resolution, blur, and brightness.
2. **Strip Detection:** Extracts the central region of the image containing the strip.
3. **Array Detection:** Divides the strip into 3 vertically aligned regions and extracts the central ROI from each.
4. **Feature Extraction:** Calculates Mean and Std Dev for RGB, HSV, and CIELAB color spaces.

## 7. How Color Matching Works
The prototype uses a simple nearest-reference color matching system based on **CIELAB ΔE76**. It calculates the Euclidean distance between the uploaded image's LAB values and each reference stage in the dataset, selecting the closest match.

## 8. How to Run the Application
Start the Streamlit dashboard:
```bash
streamlit run app.py
```

## 9. How to Add New Reference Images
1. Place the new reference image in `data/raw/`.
2. Modify `build_dataset.py` to extract the corresponding strips and assign stage numbers.
3. Re-run `build_dataset.py` to update the CSV.

## 10. How Future Calibration Data Should Be Added
Real calibration requires controlled gas chamber experiments. The future dataset should append columns for:
- `temperature`
- `humidity`
- `exposure_time`
- `H2S_ppm`
- `dose_ppm_hr`

## 11. Future ML Pipeline
Instead of nearest-neighbor, the final application will train a regression model (e.g., Random Forest, XGBoost) to predict `H2S_ppm` and `dose_ppm_hr` based on the combined feature vector of Array 1 + Array 2 + Array 3.

## 12. MLOps Architecture
A robust MLOps pipeline will be implemented using:
- **DVC:** For versioning raw images and calibration datasets.
- **MLflow:** For tracking experiments, model metrics, and model registry.

## 13. Mobile Application Roadmap
This Python/Streamlit prototype establishes the logic. The next phase involves porting the image processing and ML inference to a mobile application using **Flutter** or **React Native**, utilizing an on-device model (e.g., TensorFlow Lite).

## 14. Safety Disclaimer
This prototype uses provisional calibration labels for software demonstration. It is not a validated H₂S detector and must not be used for occupational safety decisions.

---
### HOW TO DEMONSTRATE
1. Start Streamlit (`streamlit run app.py`).
2. Upload one of the reference strip images (e.g., from `data/cropped/`).
3. Show the detected ROI.
4. Show RGB/HSV/LAB values.
5. Show nearest-stage prediction and Prototype similarity score.
6. Show the provisional H₂S value.
7. **Explain that the value is provisional.**
8. Upload another image (e.g., a slightly imperfect one from the second raw image) and demonstrate a different stage.
9. Explain how real gas-chamber calibration will replace the provisional mapping in the future.
