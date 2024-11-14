import pandas as pd
import numpy as np
import gdown

file_id = '1ebmvpP10yg-eLqQCMFG_mNin-jAe9Zly'
url = f'https://drive.google.com/uc?id={file_id}'
output = 'reviews_table.csv'

gdown.download(url, output, quiet=False)

amazon_sales = pd.read_csv("reviews_table.csv")

# Keep only category and short review column
amazon_sales = amazon_sales[['category', 'review_title']]

amazon_sales = amazon_sales.rename(columns = {'category': 'Category', 'review_title': 'review'})
amazon_sales['review'] = pd.Series(amazon_sales['review'], dtype = "string")

import nltk
from nltk.corpus import words
from nltk.tokenize import word_tokenize
import re

nltk.download('words')
nltk.download('punkt')

# Load the English word corpus into a set for fast lookups
english_words = set(nltk.corpus.words.words())

# Function to clean the reviews
def clean(text):
    # Remove special characters and punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Lowercase the text
    text = text.lower()

    # Remove non-English words
    return " ".join(w for w in nltk.wordpunct_tokenize(text) \
                    if w.lower() in english_words or not w.isalpha())


# Apply the function to the 'review' column
amazon_sales['review'] = amazon_sales['review'].apply(clean)

# Bringing in Tokenizer and a model class from transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Here, we use a variant of BERT, a pre-trained RoBERTa sentiment model
model_name = "cardiffnlp/twitter-roberta-base-sentiment" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Define sentiment labels as per according to the model
labels = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}

# Classify sentiment of the text using RoBERTa
from scipy.special import softmax
def classify(text):
    encoded_text = tokenizer(text, return_tensors = 'pt')
    output = model(**encoded_text)
    predictions = torch.nn.functional.softmax(output.logits, dim=-1)
    sentiment = torch.argmax(predictions).item()
    return labels[sentiment]

# There are a number of duplicated reviews; there are 168 duplicate occurrences
amazon_sales['review'].duplicated().value_counts()

# Extract the reviews column and store in a list
reviews = amazon_sales['review'].astype(str).tolist()

# Succesfully remove all duplicate occurrences
reviews = list(set(amazon_sales['review']))

# In general, customer satisfaction based on the reviews' overall sentiment
customer_satisfaction = []
for i in range(len(reviews)):
    review = reviews[i]
    sentiment = classify(review)
    customer_satisfaction.append(sentiment)

cust_satisfaction=pd.DataFrame({
    "Customer sentiment": customer_satisfaction
})
print(cust_satisfaction.value_counts())

# Define keywords for the other two aspects
aspect_keywords = {
    'Product Features': ["feature", "features", "design", "display", "lightweight", "size"],
    'Quality': ["quality", "defective", "broke", "reliable", "durable", "spoilt"]
}

# Function to test for Product features
def test_product_features(review):
    for pattern in aspect_keywords["Product Features"]:
        if re.search(pattern, review):
            return review
    return "N/A"

# Function to test for Quality
def test_quality(review):
    for pattern in aspect_keywords["Quality"]:
        if re.search(pattern, review):
            return review
    return "N/A"

# Function to classify sentiment of the review with respect to aspect
def run_aspect_sentiment(text):
    if text == "N/A":
        return "N/A"
    sentiment = classify(text)
    return sentiment

# Prepare lists to store insights
product_features = []
quality = []
# Process each review
for i in range(len(reviews)):
    # Categorize the review
    review=reviews[i]
    pf_review = test_product_features(review)
    quality_review = test_quality(review)

    # Run sentiment analysis on each category
    pf_sentiment = run_aspect_sentiment(pf_review)
    quality_sentiment_value = run_aspect_sentiment(quality_review)
    product_features.append(pf_sentiment)
    quality.append(quality_sentiment_value)

df = pd.DataFrame({
    "Product Features Sentiment": product_features,
    "Quality Sentiment": quality
})
sentiment_counts = {
     "Quality Sentiment": df['Quality Sentiment'].value_counts(),
    "Product Features Sentiment": df['Product Features Sentiment'].value_counts()
}
print(sentiment_counts)

# Insights of all 3 aspects collected
insights = pd.concat([df, cust_satisfaction], axis=1)
# insights.to_csv("Insights.csv", index=False)
print(insights)
