import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Sample spam dataset
data = pd.DataFrame({
    'EmailLength': [100, 300, 150, 250, 120, 600, 700, 200],
    'FreeWordFreq': [0, 5, 1, 3, 0, 10, 9, 2],
    'CapitalPercent': [5, 15, 8, 12, 4, 30, 25, 9],
    'Spam': [0, 1, 0, 1, 0, 1, 1, 0]
})

# Features and Target
X = data[['EmailLength', 'FreeWordFreq', 'CapitalPercent']]
y = data['Spam']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Train
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Predicting a new email
new_email = pd.DataFrame({
    'EmailLength': [400],
    'FreeWordFreq': [6],
    'CapitalPercent': [20]
})

result = model.predict(new_email)

if result[0] == 1:
    print("📧 The email is SPAM.")
else:
    print("📧 The email is NOT SPAM.")
