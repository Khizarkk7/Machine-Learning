import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

# Sample dataset (you can also load from CSV)
data = pd.DataFrame({
    'Age': [25, 35, 45, 32, 23, 50, 40, 60],
    'BMI': [22.5, 28.3, 31.1, 26.4, 24.2, 33.0, 30.2, 34.1],
    'BloodPressure': [120, 140, 150, 130, 125, 160, 145, 155],
    'Glucose': [85, 130, 150, 110, 95, 165, 140, 170],
    'Diabetes': [0, 1, 1, 0, 0, 1, 1, 1]
})

# Features and Target
X = data[['Age', 'BMI', 'BloodPressure', 'Glucose']]
y = data['Diabetes']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Plot BMI vs Glucose
plt.scatter(data['BMI'], data['Glucose'], c=data['Diabetes'], cmap='coolwarm')
plt.xlabel('BMI')
plt.ylabel('Glucose')
plt.title('BMI vs Glucose (Color = Diabetes)')
plt.show()
