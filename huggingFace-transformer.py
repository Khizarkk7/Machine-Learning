from transformers import pipeline

# Model load karenge
emotion_analyzer = pipeline("sentiment-analysis")

# Test sentence
result = emotion_analyzer("I love learning machine learning!")

print(result)
