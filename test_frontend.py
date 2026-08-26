import requests
import base64
import json
import cv2
import numpy as np

# Load a sample image
with open(r"c:\Users\venka\Desktop\H2S-Dosimeter-Wristband\H2S-Dosimeter\data\cropped\stage_10.jpg", "rb") as f:
    img_bytes = f.read()

# Stretch it to 480x640 to simulate frontend canvas
nparr = np.frombuffer(img_bytes, np.uint8)
img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
img_resized = cv2.resize(img, (480, 640))

# Encode to base64
_, buffer = cv2.imencode('.jpg', img_resized)
b64_str = base64.b64encode(buffer).decode('utf-8')
data_url = "data:image/jpeg;base64," + b64_str

# Send to backend
res = requests.post("http://localhost:5000/analyze", json={"image": data_url})
print(res.json())
