import cv2
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# STEP 1: Read the Pencil Sketch Image
# ---------------------------------------------------
# Read image in BGR format (OpenCV default)
sketch = cv2.imread("sketch.jpg")

# Convert BGR to RGB for correct color display
sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_BGR2RGB)

# ---------------------------------------------------
# STEP 2: Convert Sketch to Grayscale
# ---------------------------------------------------
# Pencil sketches mainly contain intensity information
gray = cv2.cvtColor(sketch_rgb, cv2.COLOR_RGB2GRAY)

# ---------------------------------------------------
# STEP 3: Remove Noise using Gaussian Blur
# ---------------------------------------------------
# This smooths the image and reduces harsh pencil noise
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# ---------------------------------------------------
# STEP 4: Detect Edges (Outline of Sketch)
# ---------------------------------------------------
# Canny edge detector extracts strong edges
edges = cv2.Canny(blur, threshold1=50, threshold2=150)

# ---------------------------------------------------
# STEP 5: Apply Color Map (Paint Effect)
# ---------------------------------------------------
# Convert grayscale sketch into a colored image
# COLORMAP_OCEAN gives a natural painting look
colored_paint = cv2.applyColorMap(gray, cv2.COLORMAP_OCEAN)

# ---------------------------------------------------
# STEP 6: Combine Color Image with Edges
# ---------------------------------------------------
# Invert edges so lines remain visible
edges_inv = cv2.bitwise_not(edges)

# Mask color image with edge map
paint_result = cv2.bitwise_and(
    colored_paint, colored_paint, mask=edges_inv
)

# ---------------------------------------------------
# STEP 7: Enhance Paint Texture using Bilateral Filter
# ---------------------------------------------------
# Bilateral filter smooths colors while preserving edges
final_paint = cv2.bilateralFilter(
    paint_result, d=9, sigmaColor=75, sigmaSpace=75
)

# ---------------------------------------------------
# STEP 8: Display All Steps
# ---------------------------------------------------
plt.figure(figsize=(12, 8))

plt.subplot(2, 3, 1)
plt.title("Original Pencil Sketch")
plt.imshow(sketch_rgb)
plt.axis("off")

plt.subplot(2, 3, 2)
plt.title("Grayscale Image")
plt.imshow(gray, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 3)
plt.title("Edge Detection")
plt.imshow(edges, cmap='gray')
plt.axis("off")

plt.subplot(2, 3, 4)
plt.title("Color Mapped Image")
plt.imshow(colored_paint)
plt.axis("off")

plt.subplot(2, 3, 5)
plt.title("Paint Effect (Before Filtering)")
plt.imshow(paint_result)
plt.axis("off")

plt.subplot(2, 3, 6)
plt.title("Final Painted Image")
plt.imshow(final_paint)
plt.axis("off")

plt.tight_layout()
plt.show()

# ---------------------------------------------------
# STEP 9: Save Final Output
# ---------------------------------------------------
cv2.imwrite("final_painted_output.jpg",
            cv2.cvtColor(final_paint, cv2.COLOR_RGB2BGR))

print("✅ Pencil Sketch successfully converted into Painting!")
