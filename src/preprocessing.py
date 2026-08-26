import cv2
import numpy as np

def validate_image(image_bytes):
    """
    Basic image validation.
    Checks if image can be decoded and basic quality (resolution).
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return False, "Invalid image format.", None
    
    # Basic quality check - resolution
    h, w = img.shape[:2]
    if h < 50 or w < 50:
        return False, "Image resolution is too low.", None
        
    # Check for excessive blur (Laplacian variance)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_val < 10:
        return False, "Image quality insufficient (excessive blur). Please retake.", None
        
    # Check for excessive darkness
    mean_brightness = np.mean(gray)
    if mean_brightness < 20:
        return False, "Image quality insufficient (too dark). Please retake.", None
        
    # Check for overexposure
    if mean_brightness > 240:
        return False, "Image quality insufficient (overexposed). Please retake.", None

    return True, "Image is valid.", img

def extract_sensing_region(img):
    """
    For the prototype, we assume the user uploads an image containing mostly the strip.
    If the image is roughly strip-proportioned (tall rectangle), we use it.
    If it's wider, we take the central crop.
    Returns the cropped strip image.
    """
    h, w = img.shape[:2]
    
    # If the image is very wide, crop the center roughly proportioned to a strip
    if w > h:
        # Expected ratio of strip is roughly 186:85 ~ 2.18 (h/w)
        target_w = int(h / 2.18)
        start_x = (w - target_w) // 2
        img = img[:, start_x:start_x+target_w]
        
    return img

def normalize_color(img):
    """
    Basic white balancing / brightness normalization.
    Currently, we implement a simple gray world assumption or just return the image
    as smartphones usually do significant auto-white-balance.
    """
    # Placeholder for advanced normalization with reference patches
    return img
