from PIL import Image
import numpy as np

img = Image.open('assets/next_level_original.png').convert('L')
pixels = np.array(img, dtype=float).flatten()
print("Min:", np.min(pixels))
print("Max:", np.max(pixels))
print("Percentiles (25, 50, 75):", np.percentile(pixels, [25, 50, 75]))
