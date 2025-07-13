import numpy as np
from collections import Counter

# Dataset
data = [
    (1, 1, 'A'),
    (2, 2, 'A'),
    (3, 3, 'B'),
    (4, 4, 'B'),
    (5, 5, 'B')
]

# New point
new_point = (3, 3)

# Calculate Euclidean distances
distances = []
for x1, x2, label in data:
    dist = np.sqrt((new_point[0] - x1) ** 2 + (new_point[1] - x2) ** 2)
    distances.append((dist, label))

# Sort and get k=3 nearest neighbors
k = 3
distances.sort()
k_nearest = distances[:k]

# Majority vote
classes = [label for _, label in k_nearest]
majority = Counter(classes).most_common(1)[0][0]

print("The new point", new_point, "is classified as:", majority)
