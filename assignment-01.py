import cv2
# import numpy as np
from matplotlib import pyplot as plt

# Load image
img = cv2.imread("apple.jpeg")

# Convert to RGB using open CV
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
l, a, b = cv2.split(lab)

clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
cl = clahe.apply(l)

# Merge channels back
enhanced_lab = cv2.merge((cl, a, b))
enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

# before/after comparision
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.title("Original")
plt.imshow(img_rgb)
plt.axis('off')

plt.subplot(1,2,2)
plt.title("Enhanced (Point Processing)")
plt.imshow(enhanced_img)
plt.axis('off')

plt.show()