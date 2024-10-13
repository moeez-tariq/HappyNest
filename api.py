from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional, Dict, List

# Load environment variables
load_dotenv()

app = FastAPI()

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
    city: str
    state: str
    country: str
    coordinates: Dict[str, float]

class User(BaseModel):
    id: Optional[str] = None # Add this so id displays in response
    name: str
    email: EmailStr
    password: str  # Will need to be hashed later
    location: Location
    streak: Optional[int] = 0
    mood: Optional[str]
    created_at: Optional[datetime] = datetime.now()

class NewsArticle(BaseModel):
    id: Optional[str] = None # Add this so id displays in response
    title: str
    content: str
    location: Location
    sentiment: str
    published_at: Optional[datetime] = datetime.now()
    source: Optional[str]

class GoodDeed(BaseModel):
    id: Optional[str] = None # Add this so id displays in response
    user_id: str  # Assumes this will be ObjectId in the database, but str here
    title: Optional[str]
    location: Location
    description: str
    completed_at: Optional[datetime] = datetime.now()
    streak_continued: Optional[bool] = False
    replies: List[str] = []  # List of reply IDs

class Reply(BaseModel):
    id: Optional[str] = None # Add this so id displays in response
    deed_id: str  # Assumes this will be ObjectId in the database
    user_id: str
    content: str
    created_at: Optional[datetime] = datetime.now()

# Helper function to handle ObjectId conversion
def str_to_objectid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

# User Endpoints
@app.post("/users/")
async def create_user(user: User):
    user_data = user.dict()
    user_data["created_at"] = datetime.now()
    result = users_collection.insert_one(user_data)
    return {"id": str(result.inserted_id)}

@app.get("/users/", response_model=List[User])
async def get_all_users():
    users = list(users_collection.find())
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user_objectid = str_to_objectid(user_id)
    user = users_collection.find_one({"_id": user_objectid})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    user_objectid = str_to_objectid(user_id)
    update_result = users_collection.update_one(
        {"_id": user_objectid},
        {"$set": user.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    user_objectid = str_to_objectid(user_id)
    delete_result = users_collection.delete_one({"_id": user_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

# Good Deed Endpoints
@app.post("/good-deeds/")
async def create_good_deed(good_deed: GoodDeed):
    good_deed_data = good_deed.dict()
    good_deed_data["completed_at"] = datetime.now()
    good_deed_data["replies"] = []
    result = good_deeds_collection.insert_one(good_deed_data)
    return {"id": str(result.inserted_id)}

@app.get("/good-deeds/", response_model=List[GoodDeed])
async def get_all_good_deeds():
    good_deeds = list(good_deeds_collection.find())
    for deed in good_deeds:
        deed["id"] = str(deed["_id"])
        del deed["_id"]
        # Fetch associated replies for each good deed
        reply_ids = deed.get("replies", [])
        deed["replies"] = [
            {**reply, "_id": str(reply["_id"])}
            for reply in replies_collection.find({"_id": {"$in": reply_ids}})
        ]
    return good_deeds

@app.get("/good-deeds/{deed_id}", response_model=GoodDeed)
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

@app.put("/good-deeds/{deed_id}")
async def update_good_deed(deed_id: str, good_deed: GoodDeed):
    deed_objectid = str_to_objectid(deed_id)
    update_result = good_deeds_collection.update_one(
        {"_id": deed_objectid},
        {"$set": good_deed.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Good deed not found")
    return {"detail": "Good deed updated successfully"}

@app.delete("/good-deeds/{deed_id}")
async def delete_good_deed(deed_id: str):
    deed_objectid = str_to_objectid(deed_id)
    delete_result = good_deeds_collection.delete_one({"_id": deed_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Good deed not found")
    return {"detail": "Good deed deleted successfully"}

# News Article Endpoints
@app.post("/news/")
async def create_news(news: NewsArticle):
    news_data = news.dict()
    news_data["published_at"] = datetime.now()
    result = news_collection.insert_one(news_data)
    return {"id": str(result.inserted_id)}

@app.get("/news/", response_model=List[NewsArticle])
async def get_all_news():
    news_articles = list(news_collection.find())
    for article in news_articles:
        article["id"] = str(article["_id"])
        del article["_id"]
    return news_articles

@app.get("/news/{article_id}", response_model=NewsArticle)
async def get_news_article(article_id: str):
    article_objectid = str_to_objectid(article_id)
    news_article = news_collection.find_one({"_id": article_objectid})
    if news_article:
        news_article["id"] = str(news_article["_id"])
        del news_article["_id"]
        return news_article
    else:
        raise HTTPException(status_code=404, detail="News article not found")

@app.put("/news/{article_id}")
async def update_news(article_id: str, news: NewsArticle):
    article_objectid = str_to_objectid(article_id)
    update_result = news_collection.update_one(
        {"_id": article_objectid},
        {"$set": news.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="News article not found")
    return {"detail": "News article updated successfully"}

@app.delete("/news/{article_id}")
async def delete_news(article_id: str):
    article_objectid = str_to_objectid(article_id)
    delete_result = news_collection.delete_one({"_id": article_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News article not found")
    return {"detail": "News article deleted successfully"}

# Reply Endpoints
@app.post("/good-deeds/{deed_id}/replies/")
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

@app.get("/good-deeds/{deed_id}/replies/")
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

@app.get("/replies/{reply_id}")
async def get_reply(reply_id: str):
    reply_objectid = str_to_objectid(reply_id)
    reply = replies_collection.find_one({"_id": reply_objectid})
    if reply:
        reply["id"] = str(reply["_id"])
        del reply["_id"]
        return reply
    else:
        raise HTTPException(status_code=404, detail="Reply not found")

@app.put("/replies/{reply_id}")
async def update_reply(reply_id: str, reply: Reply):
    reply_objectid = str_to_objectid(reply_id)
    update_result = replies_collection.update_one(
        {"_id": reply_objectid},
        {"$set": reply.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"detail": "Reply updated successfully"}

@app.delete("/replies/{reply_id}")
async def delete_reply(reply_id: str):
    reply_objectid = str_to_objectid(reply_id)
    delete_result = replies_collection.delete_one({"_id": reply_objectid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"detail": "Reply deleted successfully"}
