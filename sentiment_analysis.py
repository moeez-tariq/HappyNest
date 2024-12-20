from fastapi import FastAPI, HTTPException
from typing import List, Dict
import requests
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

API_ENDPOINT = os.getenv("OPEN_AI_API_ENDPOINT")
API_KEY = os.getenv("OPEN_AI_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
def is_political(text: str) -> bool:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that determines if text is related to politics."},
        {"role": "user", "content": f"Is this text related to politics? Answer with just 'yes' or 'no':\n\n{text}"}
    ]
    
    data = {
        "model": "gpt-3.5-turbo", 

        "messages": messages,
        "max_tokens": 10,
        "temperature": 0.3,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
        "stream": False
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Error from Azure OpenAI API: {response.text}")
    
    result = response.json()
    is_political = result["choices"][0]["message"]["content"].strip().lower() == "yes"
    return is_political

def analyze_sentiment(text: str) -> str:

    messages = [
        {"role": "system", "content": "You are a helpful assistant that performs sentiment analysis."},
        {"role": "user", "content": f"Analyze the sentiment of this text and return just one word, 'positive' if it's happy or positive, else return 'negative' if it's sad or dangerous otherwise 'neutral':\n\n{text}"}

    ]
    
    data = {
        "model": "gpt-3.5-turbo",  

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
    if sentiment == "positive" and is_political(text):
        return "neutral"
    
    return sentiment
@app.post("/analyze_sentiment/")
async def filter_happy_articles(articles: List[Dict[str, str]]):
    happy_articles = []
    for article in articles:
        sentiment = analyze_sentiment(article["content"])
        happy_articles.append(sentiment)
    
    return {"happy_articles": happy_articles}
