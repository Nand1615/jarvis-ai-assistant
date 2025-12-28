import pickle
from nlp.preprocess import clean_text

with open("ml/model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

def predict_intent(text: str):
    text = clean_text(text)
    X = vectorizer.transform([text])

    probs = model.predict_proba(X)[0]
    max_prob = max(probs)
    intent = model.classes_[probs.argmax()]

    return intent, max_prob
