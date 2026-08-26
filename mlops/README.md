# MLOps Architecture

This folder contains the framework for the future Machine Learning Operations (MLOps) pipeline.
Currently, this is a placeholder since the project relies on a non-ML nearest-color reference matching using provisional data.

## Future Architecture
1. **DVC (Data Version Control):** Will track the raw images and processed CSV datasets.
2. **MLflow:** Will track model training experiments, hyperparameters, and metrics (RMSE, MAE).
3. **Model Registry:** The best performing model will be registered in MLflow and exported to an on-device format (ONNX or TFLite) for the mobile app.

To simulate training, run `python train.py`.
