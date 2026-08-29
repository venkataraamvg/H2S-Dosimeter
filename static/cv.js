function rgb2lab(rgb) {
  let r = rgb[0] / 255, g = rgb[1] / 255, b = rgb[2] / 255;
  r = (r > 0.04045) ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
  g = (g > 0.04045) ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
  b = (b > 0.04045) ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

  let x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047;
  let y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) / 1.00000;
  let z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883;

  x = (x > 0.008856) ? Math.pow(x, 1/3) : (7.787 * x) + 16/116;
  y = (y > 0.008856) ? Math.pow(y, 1/3) : (7.787 * y) + 16/116;
  z = (z > 0.008856) ? Math.pow(z, 1/3) : (7.787 * z) + 16/116;

  return [(116 * y) - 16, 500 * (x - y), 200 * (y - z)];
}

function calcDeltaE(labA, labB) {
  const deltaL = labA[0] - labB[0];
  const deltaA = labA[1] - labB[1];
  const deltaB = labA[2] - labB[2];
  return Math.sqrt(deltaL * deltaL + deltaA * deltaA + deltaB * deltaB);
}

function processClientSideCV(canvas) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  // Exact coordinates matching the UI guides (and python backend)
  const regions = {
    fast: { x: 0.27, y: 0.15, w: 0.22, h: 0.14 },
    medium: { x: 0.27, y: 0.43, w: 0.22, h: 0.14 },
    slow: { x: 0.27, y: 0.71, w: 0.22, h: 0.14 }
  };

  const colors = {};
  const labs = {};

  // Extract mean RGB for each region
  Object.keys(regions).forEach((key, idx) => {
    const r = regions[key];
    const rx = Math.floor(r.x * w);
    const ry = Math.floor(r.y * h);
    const rw = Math.floor(r.w * w);
    const rh = Math.floor(r.h * h);

    const imgData = ctx.getImageData(rx, ry, rw, rh).data;
    let sumR = 0, sumG = 0, sumB = 0;
    const pixelCount = rw * rh;

    for (let i = 0; i < imgData.length; i += 4) {
      sumR += imgData[i];
      sumG += imgData[i + 1];
      sumB += imgData[i + 2];
    }

    const meanR = sumR / pixelCount;
    const meanG = sumG / pixelCount;
    const meanB = sumB / pixelCount;

    colors[key] = [meanR, meanG, meanB];
    
    // Convert to OpenCV scaled LAB so it matches our dataset exactly.
    // OpenCV CIELAB scales L to 0..255 (L*255/100), and a/b to 0..255 (a+128, b+128)
    const rawLab = rgb2lab(colors[key]);
    labs[key] = [
        rawLab[0] * 2.55, 
        rawLab[1] + 128, 
        rawLab[2] + 128
    ];
  });

  // Calculate distance to reference stages
  let bestStage = 1;
  let minAvgDist = Infinity;
  const stageDistances = {};

  for (const [stage, ref] of Object.entries(REFERENCE_DATA)) {
    const d1 = calcDeltaE(labs.fast, [ref.array_1_L, ref.array_1_a, ref.array_1_b]);
    const d2 = calcDeltaE(labs.medium, [ref.array_2_L, ref.array_2_a, ref.array_2_b]);
    const d3 = calcDeltaE(labs.slow, [ref.array_3_L, ref.array_3_a, ref.array_3_b]);
    
    const avgDist = (d1 + d2 + d3) / 3;
    stageDistances[stage] = { avg: avgDist, d1, d2, d3 };

    if (avgDist < minAvgDist) {
      minAvgDist = avgDist;
      bestStage = parseInt(stage);
    }
  }

  // Provisional calibration table
  const PROVISIONAL_CALIBRATION = {
    1: 0, 2: 0.5, 3: 1, 4: 2, 5: 3, 6: 4, 
    7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10
  };
  
  const ppm = PROVISIONAL_CALIBRATION[bestStage] || 0;
  let risk = "LOW";
  if (ppm >= 5) risk = "HIGH";
  else if (ppm >= 2) risk = "MEDIUM";

  return {
    colours: colors,
    exposureResult: {
      exposure: ppm,
      riskLevel: risk,
      deltaEs: {
        fast: stageDistances[bestStage].d1,
        medium: stageDistances[bestStage].d2,
        slow: stageDistances[bestStage].d3
      }
    },
    backend_info: {
      stage: bestStage,
      similarity: 100 - minAvgDist,
      min_dist: minAvgDist
    }
  };
}
