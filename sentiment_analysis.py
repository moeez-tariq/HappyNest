from fastapi import FastAPI, HTTPException
from typing import List, Dict
import requests
import os

app = FastAPI()

API_ENDPOINT = "https://basil-ahmed.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview"
API_KEY = "4pxcDXzlXD7iOXPehEormDW4ih2vamQ7ufkQ0Xq7WsSZ8gcq71hiJQQJ99AKACYeBjFXJ3w3AAABACOGW3Zj"

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

def analyze_sentiment(text: str) -> str:
    # Use the chat format for Azure OpenAI API
    messages = [
        {"role": "system", "content": "You are a helpful assistant that performs sentiment analysis."},
        {"role": "user", "content": f"Analyze the sentiment of this text and return just one word, 'positive' if it's happy or positive, else return 'negative' if it's sad or dangerous otherwise 'neutral':\n\n{text}"}
    ]
    
    data = {
        "messages": messages,
        "max_tokens":800,  
        "temperature":0.7,  
        "top_p":0.95,  
        "frequency_penalty":0,  
        "presence_penalty":0,  
        "stop":None,  
        "stream":False  
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Error from Azure OpenAI API: {response.text}")
        
    
    result = response.json()
    sentiment = result["choices"][0]["message"]["content"].strip().lower()
    return sentiment

@app.post("/analyze_sentiment/")
async def filter_happy_articles(articles: List[Dict[str, str]]):
    happy_articles = []
    for article in articles:
        sentiment = analyze_sentiment(article["content"])
        happy_articles.append(sentiment)
    
    return {"happy_articles": happy_articles}