import cv2
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------
# STEP 1: Read the Colored Painting Image
# ---------------------------------------------------
# Load image (OpenCV loads in BGR format)
img = cv2.imread("painting.jpg")

# Convert BGR to RGB for correct color display
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# ---------------------------------------------------
# STEP 2: Convert Image to Grayscale
# ---------------------------------------------------
# Pencil sketches are intensity based, not color based
gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

# ---------------------------------------------------
# STEP 3: Invert the Grayscale Image
# ---------------------------------------------------
# Inversion simulates white paper background
inverted = 255 - gray

# ---------------------------------------------------
# STEP 4: Apply Gaussian Blur
# ---------------------------------------------------
# Blurring spreads pencil strokes smoothly
blur = cv2.GaussianBlur(inverted, (21, 21), 0)

# ---------------------------------------------------
# STEP 5: Dodge Blending (Core Pencil Sketch Formula)
# ---------------------------------------------------
# This formula enhances edges and creates sketch strokes
# sketch = gray / (255 - blur)
sketch = cv2.divide(gray, 255 - blur, scale=256)

# ---------------------------------------------------
# STEP 6: Improve Sketch Quality (Optional Filtering)
# ---------------------------------------------------
# Median filter removes unwanted noise
sketch_clean = cv2.medianBlur(sketch, 5)

# ---------------------------------------------------
# STEP 7: Display All Processing Stages
# ---------------------------------------------------
plt.figure(figsize=(12, 8))

plt.subplot(2, 3, 1)
plt.title("Original Painting")
plt.imshow(img_rgb)
plt.axis("off")

plt.subplot(2, 3, 2)
plt.title("Grayscale Image")
plt.imshow(gray, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 3)
plt.title("Inverted Image")
plt.imshow(inverted, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 4)
plt.title("Blurred Inverted Image")
plt.imshow(blur, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 5)
plt.title("Raw Pencil Sketch")
plt.imshow(sketch, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 6)
plt.title("Final Pencil Sketch")
plt.imshow(sketch_clean, cmap='gray')
plt.axis("off")

plt.tight_layout()
plt.show()

# ---------------------------------------------------
# STEP 8: Save Final Sketch Output
# ---------------------------------------------------
cv2.imwrite("painting_to_pencil_sketch.jpg", sketch_clean)

print("✅ Painting successfully converted into Pencil Sketch!")
