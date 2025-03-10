# modules/sentiment_analysis.py
from transformers import BertTokenizer, BertForSequenceClassification
from scipy.special import softmax
import pandas as pd

MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)

def get_sentiment_score(text):
    """
    Analyze sentiment using BERT model and return sentiment score.
    The sentiment score is rounded to 2 decimal places.
    """
    if not text.strip():
        return "Neutral", 0.5  # Default for empty text
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    scores = outputs.logits.detach().numpy()[0]
    probabilities = softmax(scores)

    sentiment_labels = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]
    sentiment_index = probabilities.argmax()
    
    # Round the sentiment score to 2 decimal places
    sentiment_score = round(probabilities[sentiment_index], 2)
    
    return sentiment_labels[sentiment_index], sentiment_score

def analyze_resume_sentiment(df):
    """
    Reads a resume dataset, extracts key sections, and performs sentiment analysis.
    The sentiment score is rounded to 2 decimal places before converting to a percentage.
    """
    sentiment_results = []

    for _, row in df.iterrows():
        candidate_name = row.get("name", "Unknown Candidate")
        career_objective = row.get("career_objective", "")
        skills = row.get("skills", "")
        work_experience = row.get("experience", "")
        extra_curricular = row.get("extra_curricular", "")

        # Combine all text sections
        resume_text = f"{career_objective} {skills} {work_experience} {extra_curricular}"

        # Perform Sentiment Analysis
        sentiment_label, sentiment_score = get_sentiment_score(resume_text)

        # Store result
        sentiment_results.append({
            "Name": candidate_name,
            "Sentiment": sentiment_label,
            "Sentiment Score": round(sentiment_score * 100, 2)  # Convert to percentage and round to 2 decimal places
        })

    return pd.DataFrame(sentiment_results)