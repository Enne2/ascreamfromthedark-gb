from PIL import Image
import numpy as np
from scipy.cluster.vq import kmeans, vq

# Open original and convert to grayscale
img = Image.open('assets/next_level_original.png').convert('L')
pixels = np.array(img, dtype=float)

# Flatten for clustering
flat_pixels = pixels.flatten()

# Find 4 clusters
centroids, _ = kmeans(flat_pixels, 4)

# Sort centroids by brightness (dark to light)
sorted_centroids = np.sort(centroids)

# Map centroids to GB colors
# GB palette: 0=Black, 1=Dark Gray, 2=Light Gray, 3=White
gb_colors = np.array([0, 85, 170, 255])

# Find the closest centroid for each pixel
# Assign the corresponding GB color
quantized_pixels = np.zeros_like(flat_pixels, dtype=np.uint8)
for i, p in enumerate(flat_pixels):
    dist = np.abs(sorted_centroids - p)
    closest_idx = np.argmin(dist)
    quantized_pixels[i] = gb_colors[closest_idx]

# Reshape back to image
quantized_img_data = quantized_pixels.reshape(pixels.shape)
new_img = Image.fromarray(quantized_img_data, mode='L').convert('RGB')
new_img.save('assets/next_level.png')
print("Processed next_level.png with k-means clustering!")
