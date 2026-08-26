# src/config.py

# Provisional mapping for the prototype demonstration ONLY.
# NOT LABORATORY CALIBRATED.
#
# These values are used solely to demonstrate the software capability.

PROVISIONAL_CALIBRATION = {
    1: 0,
    2: 0.5,
    3: 1,
    4: 2,
    5: 3,
    6: 5,
    7: 7,
    8: 10,
    9: 15,
    10: 20,
    11: 30,
    12: 50
}

# Unit conversion (mg/m3 = ppm * 1.394)
PPM_TO_MGM3 = 1.394

# Prototype Exposure Categories (Provisional visualization)
def get_exposure_category(ppm):
    if ppm < 5:
        return "Low"
    elif ppm < 15:
        return "Moderate"
    else:
        return "High"

# Warning message
DISCLAIMER = "WARNING: This prototype uses provisional calibration labels for software demonstration. It is not a validated H₂S detector and must not be used for occupational safety decisions."
