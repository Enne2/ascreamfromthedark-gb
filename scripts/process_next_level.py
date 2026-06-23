from PIL import Image
import numpy as np

# Open original and convert to grayscale
img = Image.open('assets/next_level_original.png').convert('L')
pixels = np.array(img, dtype=np.uint8)

# Fixed thresholds for Game Boy colors
quantized_pixels = np.zeros_like(pixels)

# Map based on standard thresholds to preserve darkness
quantized_pixels[pixels < 40] = 0           # Black
quantized_pixels[(pixels >= 40) & (pixels < 128)] = 85   # Dark Gray
quantized_pixels[(pixels >= 128) & (pixels < 200)] = 170 # Light Gray
quantized_pixels[pixels >= 200] = 255       # White

# Reshape back to image
new_img = Image.fromarray(quantized_pixels, mode='L').convert('RGB')
new_img.save('assets/next_level.png')
print("Processed next_level.png with fixed thresholds!")
