from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from difflib import SequenceMatcher
import os
import random
import time
import requests
from pprint import pprint
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Access environment variables
USERNAME = os.getenv("AYLIEN_USERNAME")
PASSWORD = os.getenv("AYLIEN_PASSWORD")
APP_ID = os.getenv("AYLIEN_APP_ID")
OPEN_AI_API_ENDPOINT = os.getenv("OPEN_AI_API_ENDPOINT")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")  

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://happynest-kappa.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MongoDB connection setup
MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    print("Databases available:")
    print(client.list_database_names())
    db = client.get_database("HappyNest")  # HappyNest database
    users_collection = db.get_collection("users")
    news_collection = db.get_collection("news")
    good_deeds_collection = db.get_collection("good_deeds")
    replies_collection = db.get_collection("replies")

    client.server_info()  # Force the client to connect to the server
    print("Connected successfully to the 'HappyNest' database!")
except errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)

# Models
class Location(BaseModel):
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    coordinates: Optional[Dict[str, float]]

class User(BaseModel):
    id: Optional[str] = None # Add this so id displays in response
    name: str
    email: EmailStr
    password: str  # Will need to be hashed later
    location: Optional[Location]
    streak: Optional[int] = 0
    mood: Optional[str]
    created_at: Optional[datetime] = datetime.now()

class NewsArticle(BaseModel):
    id: Optional[str] #= None # Add this so id displays in response
    title: Optional[str]
    content: Optional[str]
    location: Optional[Location]
    sentiment: Optional[str]
    published_at: Optional[datetime] #= datetime.now()
    source: Optional[str]

class Reply(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    deed_id: str
    user_id: str
    content: str
    created_at: Optional[datetime] = datetime.now()
    
class GoodDeed(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: Optional[str]
    location: Optional[Location]
    description: str
    completed_at: Optional[datetime] = datetime.now()
    streak_continued: Optional[bool] = False
    replies: List[Reply] = []

# Helper function to handle ObjectId conversion
def str_to_objectid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    
def get_auth_header(username, password, appid):
    # Generate the authorization header for making requests to the Aylien API.
    token = requests.post('https://api.aylien.com/v1/oauth/token', auth=(username, password), data={'grant_type': 'password'})
    token = token.json()['access_token']
    headers = {f'Authorization': 'Bearer {}'.format(token), 'AppId': appid}
    return headers
# Function to calculate similarity
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
# Function to remove duplicates based on a given threshold
def remove_duplicates(stories, threshold=0.5):
    unique_stories = []
    seen_titles = []
    for story in stories:
        title = story['title']
        if not any(similar(title, seen_title) > threshold for seen_title in seen_titles):
            unique_stories.append(story)
            seen_titles.append(title)
    return unique_stories
def get_top_stories(params, headers, n_top_stories=False):
    fetched_stories = []
    stories = None
    if 'per_page' in params.keys():
        if params['per_page'] > n_top_stories and not n_top_stories == False:
            params['per_page'] = n_top_stories
    while (
        stories is None
        or len(stories) > 0
        and (len(fetched_stories) < n_top_stories or n_top_stories == False)
    ):
        try:
            response = requests.get('https://api.aylien.com/v6/news/stories', params=params, headers=headers)
            # If the call is successfull it will append it
            if response.status_code == 200:
                response_json = response.json()
                stories = response_json['stories']
                if 'next_page_cursor' in response_json.keys():
                    params['cursor'] = response_json['next_page_cursor']
                else:
                    pprint('No next_page_cursor')
                fetched_stories += stories
                if len(stories) > 0 and not stories == None:
                    print(
                        'Fetched %d stories. Total story count so far: %d'
                        % (len(stories), len(fetched_stories))
                    )
            # If the application reached the limit per minute it will sleep and retry until the limit is reset
            elif response.status_code == 429:
                time.sleep(10)
                continue
            # If the API call face network or server errors it sleep for few minutes and try again a few times until completely stop the script.
            elif 500 <= response.status_code <= 599:
                time.sleep(260)
                continue
            # If the API call return any other status code it return the error for futher investigation and stop the script.
            else:
                pprint(response.text)
                break
        except Exception as e:
            # In case the code fall in any exception error.
            pprint(e)
            break
    return fetched_stories
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPEN_AI_API_KEY}"
}
def is_political(text: str) -> bool:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that determines if text is related to politics and you just answer in one word."},
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

    response = requests.post(OPEN_AI_API_ENDPOINT, headers=headers, json=data)
    
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
        "stop": None,  
        "stream": False  
    }

    response = requests.post(OPEN_AI_API_ENDPOINT, headers=headers, json=data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Error from OpenAI API: {response.text}")
        
    
    result = response.json()
    sentiment = result["choices"][0]["message"]["content"].strip().lower()
    if sentiment == "positive" and is_political(text):
        return "neutral"
    
    return sentiment

# User Endpoints
@app.post("/api/users/")
async def create_user(user_data: dict):
   try:
       # Check if user exists
       existing_user = users_collection.find_one({"_id": user_data["_id"]})
       if existing_user:
           return {"message": "User already exists"}

       # Add created_at timestamp
       user_data["created_at"] = datetime.now()
       
       # Insert new user
       result = users_collection.insert_one(user_data)
       return {"id": user_data["_id"]}
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/", response_model=List[User])
async def get_all_users():
    users = list(users_collection.find())
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = users_collection.find_one({"_id": user_id})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user: User):
    user_objectid = str_to_objectid(user_id)
    update_result = users_collection.update_one(
        {"_id": user_objectid},
        {"$set": user.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User updated successfully"}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    user_objectid = str_to_objectid(user_id)
    delete_result = users_collection.delete_one({"_id": user_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

# Good Deed Endpoints
@app.post("/api/good-deeds/")
async def create_good_deed(good_deed: GoodDeed):
    good_deed_data = good_deed.dict()
    good_deed_data["completed_at"] = datetime.now()
    good_deed_data["replies"] = []
    result = good_deeds_collection.insert_one(good_deed_data)
    return {"id": str(result.inserted_id)}

@app.get("/api/good-deeds/", response_model=List[GoodDeed])
async def get_all_good_deeds():
    good_deeds = list(good_deeds_collection.find())
    for deed in good_deeds:
        deed["id"] = str(deed["_id"])
        del deed["_id"]
        # Convert reply IDs to actual reply objects
        if "replies" in deed:
            reply_ids = [str_to_objectid(rid) for rid in deed["replies"]]
            deed["replies"] = list(replies_collection.find({"_id": {"$in": reply_ids}}))
            # Clean up reply objects
            for reply in deed["replies"]:
                reply["id"] = str(reply["_id"])
                del reply["_id"]
    return good_deeds

@app.get("/api/good-deeds/{deed_id}", response_model=GoodDeed)
async def get_good_deed(deed_id: str):
    deed_objectid = str_to_objectid(deed_id)
    good_deed = good_deeds_collection.find_one({"_id": deed_objectid})
    if good_deed:
        good_deed["id"] = str(good_deed["_id"])
        del good_deed["_id"]
        # Fetch associated replies
        reply_ids = good_deed.get("replies", [])
        good_deed["replies"] = [
            {**reply, "_id": str(reply["_id"])}
            for reply in replies_collection.find({"_id": {"$in": reply_ids}})
        ]
        return good_deed
    else:
        raise HTTPException(status_code=404, detail="Good deed not found")

@app.put("/api/good-deeds/{deed_id}")
async def update_good_deed(deed_id: str, good_deed: GoodDeed):
    deed_objectid = str_to_objectid(deed_id)
    update_result = good_deeds_collection.update_one(
        {"_id": deed_objectid},
        {"$set": good_deed.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Good deed not found")
    return {"detail": "Good deed updated successfully"}

@app.delete("/api/good-deeds/{deed_id}")
async def delete_good_deed(deed_id: str):
    deed_objectid = str_to_objectid(deed_id)
    delete_result = good_deeds_collection.delete_one({"_id": deed_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Good deed not found")
    return {"detail": "Good deed deleted successfully"}

# News Article Endpoints
@app.post("/api/news/")
async def create_news(news: NewsArticle):
    try:
        news_data = news.dict()
        # print(f"Received news data: {news.dict()}")
        news_data["published_at"] = datetime.now()
        result = news_collection.insert_one(news_data)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error creating news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

os.makedirs('audio', exist_ok=True)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")



client2 = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

@app.get("/api/news/global-fetch", response_model=List[NewsArticle])
async def fetch_news_global():
    try:
        cities = [
            "New York", "Los Angeles", "Chicago", "San Francisco", "Miami", "Houston", "Boston", "Seattle",
            "London", "Paris", "Berlin", "Rome", "Madrid", "Barcelona", "Amsterdam", "Vienna", "Zurich",
            "Tokyo", "Osaka", "Kyoto", "Seoul", "Beijing", "Shanghai", "Hong Kong", "Singapore", 
            "Sydney", "Melbourne", "Brisbane", "Auckland", "Toronto", "Vancouver", "Montreal", "Ottawa",
            "Dubai", "Abu Dhabi", "Cairo", "Cape Town", "Lagos", "Nairobi", "Mumbai", "Delhi", "Bangalore",
            "Mexico City", "Buenos Aires", "Rio de Janeiro", "Sao Paulo", "Lima", "Bogota", "Caracas", 
            "Jakarta", "Manila", "Kuala Lumpur", "Bangkok", "Ho Chi Minh City", "Istanbul"
        ]
        
        selected_cities = random.sample(cities, k=4)
        print(f"Fetching news for cities: {selected_cities}")

        all_news = []

        for city in selected_cities:
            headers = get_auth_header(USERNAME, PASSWORD, APP_ID)
            params = {
                "published_at": "[NOW-14DAYS/HOUR TO NOW/HOUR]",
                "language": "(en)",
                "entities": '{{element:title AND surface_forms:"' + city + '" AND type:("Location", "City")}}',
                "sort_by": "published_at",
                "per_page": 11,
            }

            stories = get_top_stories(params, headers, 11)
            if not stories:
                continue

            deduplicated_stories = remove_duplicates(stories, threshold=0.5)

            for story in deduplicated_stories:
                try:
                    news_data = {
                        "title": story["title"],
                        "content": story["body"],
                        "location": {
                            "city": city,
                            "state": "Unknown",
                            "country": "Unknown",
                            "coordinates": {
                                "latitude": 0,
                                "longitude": 0
                            }
                        },
                        "published_at": datetime.utcnow(),
                        "source": story["links"]["permalink"],
                        "id": str(ObjectId())
                    }

                    sentiment = analyze_sentiment(news_data["content"])
                    news_data["sentiment"] = sentiment

                    if sentiment == "positive":
                        all_news.append(news_data)

                except Exception as story_error:
                    # print(f"Error processing story: {story_error}")
                    continue

        random.shuffle(all_news)
        combined_news_content = (
            "Welcome to HappyNest Radio, your daily dose of positivity and inspiration, "
            "where we bring you the latest headlines to keep you informed and uplifted.\n\n"
        )
        for article in all_news:
            combined_news_content +=  f"{article['title']}\n\n"  # Adding 'Headline:' for clarity and emphasis

        combined_news_content += (
            "That wraps up today's HappyNest Radio broadcast. "
            "Thank you for tuning in, and remember to spread kindness and stay informed!"
        )
        speech_file_path = Path("audio") / "combined_news_audio.mp3"
        os.makedirs("audio", exist_ok=True)

        response = client2.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=combined_news_content
        )

        response.stream_to_file(speech_file_path)

        audio_url = f"/audio/combined_news_audio.mp3"
        print(audio_url)

        return all_news

    except Exception as e:
        print(f"Fetch news error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching news: {str(e)}"
        )


@app.get("/api/news/", response_model=Any)
async def fetch_news():
    try:
        # Calculate the date 14 days ago
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Query the database for news articles published within the last 14 days
        news_articles = news_collection.find({"published_at": {"$gte": seven_days_ago}}).sort("published_at", -1)
        all_news = []
        
        # Convert MongoDB cursor to a list of dictionaries
        for article in news_articles:
            news_data = {
                        "title": article["title"],
                        "content": article["content"],
                        "location": {
                            "city": article["location"]["city"],
                            "state": "Unknown",
                            "country": "Unknown",
                            "coordinates": {
                                "latitude": 0,
                                "longitude": 0
                            }
                        },
                        "published_at": article["published_at"],
                        "source": article["source"],
                        "id": str(ObjectId())
                    }
            all_news.append(news_data)
        all_news = all_news[:40]

        random.shuffle(all_news)

        return all_news

    except Exception as e:
        print(f"Fetch news error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching news: {str(e)}"
        )


@app.get("/api/news/location", response_model=Any)
async def get_location_news(lat: Optional[float] = None, lon: Optional[float] = None):
    try:
        city = "New York"  # Default city
        if lat is not None and lon is not None:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
            response = requests.get(url, headers={'User-Agent': 'YourApp/1.0'})
            data = response.json()
            if 'address' in data:
                city = data['address'].get('city') or data['address'].get('town') or data['address'].get('village')
                if city and 'City of' in city:
                    city = city[8:]

        # Calculate the date 14 days ago
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Query the database for news articles published within the last 14 days and by city
        news_articles = news_collection.find({"published_at": {"$gte": seven_days_ago}, "location.city": city}).sort("published_at", -1)
        all_news = []
        
        # Convert MongoDB cursor to a list of dictionaries
        for article in news_articles:
            news_data = {
                        "title": article["title"],
                        "content": article["content"],
                        "location": {
                            "city": article["location"]["city"],
                            "state": "Unknown",
                            "country": "Unknown",
                            "coordinates": {
                                "latitude": 0,
                                "longitude": 0
                            }
                        },
                        "published_at": article["published_at"],
                        "source": article["source"],
                        "id": str(ObjectId())
                    }
            all_news.append(news_data)

        # first 40
        all_news = all_news[:40]

        random.shuffle(all_news)

        return all_news
    
    except Exception as e:
        print(f"Fetch news error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching news: {str(e)}"
        )

@app.get("/api/news/fetch", response_model=List[NewsArticle])
async def fetch_news(lat: Optional[float] = None, lon: Optional[float] = None):
    try:
        city = "New York"  # Default city
        if lat is not None and lon is not None:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
            response = requests.get(url, headers={'User-Agent': 'YourApp/1.0'})
            data = response.json()
            if 'address' in data:
                city = data['address'].get('city') or data['address'].get('town') or data['address'].get('village')
                if city and 'City of' in city:
                    city = city[8:]
      
        headers = get_auth_header(USERNAME, PASSWORD, APP_ID)
        params = {
            "published_at": "[NOW-14DAYS/HOUR TO NOW/HOUR]",
            "language": "(en)",
            "entities": '{{element:title AND surface_forms:"' + city + '" AND type:("Location", "City")}}',
            "sort_by": "published_at",
            "per_page": 20,
        }

        stories = get_top_stories(params, headers, 20)
        if not stories:
            return []
        deduplicated_stories = remove_duplicates(stories, threshold=0.5)
        positive_news = []
        
        for story in deduplicated_stories:
            try:   
                news_data = {
                    "title": story["title"],
                    "content": story["body"],
                    "location": {
                        "city": city,
                        "state": "Unknown",
                        "country": "Unknown",
                        "coordinates": {
                            "latitude": lat if lat is not None else 0,
                            "longitude": lon if lon is not None else 0
                        }
                    },
                    "published_at": datetime.utcnow(),
                    "source": story["links"]["permalink"],
                    "id": str(ObjectId())  # Generate a unique ID
                }
                
                sentiment = analyze_sentiment(news_data["content"])
                news_data["sentiment"] = sentiment
                
                if sentiment == "positive":
                    positive_news.append(news_data)
                    news_collection.insert_one(news_data)
                    
            except Exception as story_error:
                print(f"Error processing story: {story_error}")
                continue
         
       # Limit to 10 positive news headlines
        positive_news = positive_news[:10]

        combined_news_content = (
            "Welcome to HappyNest Local Radio, your source for uplifting news and positive updates in your area. "
            "Here are the latest heartwarming stories:\n\n"
        )

        for article in positive_news:
            combined_news_content += f"{article['title']}\n\n"

        # Final wrap-up message
        combined_news_content += (
            "That concludes today's updates on HappyNest Local Radio. Stay positive, stay informed, and we'll be back soon with more good news!"
        )
        # Path to save the generated audio file
        speech_file_path = Path("audio") / f"local_news_{city.replace(' ', '_')}.mp3"
        os.makedirs("audio", exist_ok=True)

        # Generate speech using OpenAI TTS
        response = client2.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=combined_news_content
        )

        # Save the audio file to the defined path
        response.stream_to_file(speech_file_path)

        # Return the audio file URL
        audio_url = f"/audio/{speech_file_path.name}"
        print(f"Audio file generated: {audio_url}")
        
        return positive_news

    except Exception as e:
        print(f"Fetch news error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching news: {str(e)}"
        )
    







@app.get("/api/news/{article_id}", response_model=NewsArticle)
async def get_news_article(article_id: str):
    article_objectid = str_to_objectid(article_id)
    news_article = news_collection.find_one({"_id": article_objectid})
    if news_article:
        news_article["id"] = str(news_article["_id"])
        del news_article["_id"]
        return news_article
    else:
        raise HTTPException(status_code=404, detail="News article not found")

@app.put("/api/news/{article_id}")
async def update_news(article_id: str, news: NewsArticle):
    article_objectid = str_to_objectid(article_id)
    update_result = news_collection.update_one(
        {"_id": article_objectid},
        {"$set": news.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="News article not found")
    return {"detail": "News article updated successfully"}

@app.delete("/api/news/{article_id}")
async def delete_news(article_id: str):
    article_objectid = str_to_objectid(article_id)
    delete_result = news_collection.delete_one({"_id": article_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News article not found")
    return {"detail": "News article deleted successfully"}

# Reply Endpoints
@app.post("/api/good-deeds/{deed_id}/replies/")
async def create_reply(deed_id: str, reply: Reply):
    # Convert Good Deed ID to ObjectId and find the good deed
    good_deed_objectid = str_to_objectid(deed_id)
    good_deed = good_deeds_collection.find_one({"_id": good_deed_objectid})
    if not good_deed:
        raise HTTPException(status_code=404, detail="Good deed not found")

    # Insert the new reply
    reply_data = reply.dict()
    reply_data["deed_id"] = deed_id
    reply_data["created_at"] = datetime.now()
    result = replies_collection.insert_one(reply_data)

    # Update the good deed's replies array with the new reply's ID
    good_deeds_collection.update_one(
        {"_id": good_deed_objectid},
        {"$push": {"replies": str(result.inserted_id)}}
    )

    return {"reply_id": str(result.inserted_id)}

@app.get("/api/good-deeds/{deed_id}/replies/")
async def get_all_replies(deed_id: str):
    good_deed_objectid = str_to_objectid(deed_id)
    good_deed = good_deeds_collection.find_one({"_id": good_deed_objectid})
    if not good_deed:
        raise HTTPException(status_code=404, detail="Good deed not found")

    reply_ids = good_deed.get("replies", [])
    replies = list(replies_collection.find({"_id": {"$in": [str_to_objectid(rid) for rid in reply_ids]}}))
    for reply in replies:
        reply["id"] = str(reply["_id"])
        del reply["_id"]
    return replies

@app.get("/api/replies/{reply_id}")
async def get_reply(reply_id: str):
    reply_objectid = str_to_objectid(reply_id)
    reply = replies_collection.find_one({"_id": reply_objectid})
    if reply:
        reply["id"] = str(reply["_id"])
        del reply["_id"]
        return reply
    else:
        raise HTTPException(status_code=404, detail="Reply not found")

@app.put("/api/replies/{reply_id}")
async def update_reply(reply_id: str, reply: Reply):
    reply_objectid = str_to_objectid(reply_id)
    update_result = replies_collection.update_one(
        {"_id": reply_objectid},
        {"$set": reply.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"detail": "Reply updated successfully"}

@app.delete("/api/replies/{reply_id}")
async def delete_reply(reply_id: str):
    reply_objectid = str_to_objectid(reply_id)
    delete_result = replies_collection.delete_one({"_id": reply_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"detail": "Reply deleted successfully"}

@app.get("/api/leaderboard/")
async def get_leaderboard():
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",  # Groups deeds by user_id
                "deed_count": {"$sum": 1}  # Counts deeds per user
            }
        },
        {"$sort": {"deed_count": -1}},  # Sort by highest count
        {"$limit": 10}  # Get top 10
    ]
    
    deed_counts = list(good_deeds_collection.aggregate(pipeline))
    
    # Get user details
    leaders = []
    for deed_count in deed_counts:
        user = users_collection.find_one({"_id": deed_count["_id"]})  # Changed to match new format
        
        if user:
            leaders.append({
                "user_id": deed_count["_id"],
                "deed_count": deed_count["deed_count"],
                "name": user["name"],
                "streak": user["streak"],
                "mood": user["mood"]
            })
    
    return leaders


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)