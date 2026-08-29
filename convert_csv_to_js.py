import pandas as pd
import json

df = pd.read_csv(r"c:\Users\venka\Desktop\H2S-Dosimeter-Wristband\H2S-Dosimeter\data\processed\h2s_dataset.csv")

js_data = {}
for _, row in df.iterrows():
    stage = int(row['stage'])
    js_data[stage] = {
        'array_1_L': row['array_1_L'],
        'array_1_a': row['array_1_a'],
        'array_1_b': row['array_1_b'],
        'array_2_L': row['array_2_L'],
        'array_2_a': row['array_2_a'],
        'array_2_b': row['array_2_b'],
        'array_3_L': row['array_3_L'],
        'array_3_a': row['array_3_a'],
        'array_3_b': row['array_3_b'],
    }

print("const REFERENCE_DATA =", json.dumps(js_data, indent=2) + ";")
