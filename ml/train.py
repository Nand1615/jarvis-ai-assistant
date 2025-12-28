import json
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from nlp.preprocess import clean_text


# Load training data
with open("data/intents.json", "r") as f:
    intents = json.load(f)

sentences = []
labels = []

for intent, examples in intents.items():
    for example in examples:
        sentences.append(clean_text(example))
        labels.append(intent)

# Convert text to numbers
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(sentences)

# Train model
model = MultinomialNB()
model.fit(X, labels)

# Save model
with open("ml/model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("ML intent model trained and saved successfully.")
