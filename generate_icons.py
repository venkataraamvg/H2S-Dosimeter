import cv2
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")

# 192x192 icon
img_192 = np.zeros((192, 192, 3), dtype=np.uint8)
img_192[:] = (134, 124, 14) # Teal (BGR format)
cv2.circle(img_192, (96, 96), 60, (255, 255, 255), -1)
cv2.imwrite(os.path.join(static_dir, "icon-192.png"), img_192)

# 512x512 icon
img_512 = np.zeros((512, 512, 3), dtype=np.uint8)
img_512[:] = (134, 124, 14) # Teal
cv2.circle(img_512, (256, 256), 160, (255, 255, 255), -1)
cv2.imwrite(os.path.join(static_dir, "icon-512.png"), img_512)
