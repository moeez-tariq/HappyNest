import os
from dotenv import load_dotenv
import pymongo
import re
from bson.objectid import ObjectId
from datetime import datetime
import random
from datetime import datetime, timedelta
load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')
print(mongodb_uri)

# Connect to MongoDB
try:
    client = pymongo.MongoClient(mongodb_uri)
    print("Databases available:")
    print(client.list_database_names())
    db = client.get_database("HappyNest")  # HappyNest database
    users = db.get_collection("users")
    news = db.get_collection("news")
    good_deeds = db.get_collection("good_deeds")
    replies = db.get_collection("replies")

    client.server_info()  # Force the client to connect to the server
    print("Connected successfully to the 'HappyNest' database!")
except pymongo.errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    exit(1)

def add_good_deed():
    user_id = input("Enter user ID: ")
    title = input("Enter good deed title: ")
    city = input("Enter city: ")
    state = input("Enter state: ")
    country = input("Enter country: ")
    
    # Prompt for coordinates (latitude and longitude)
    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    description = input("Enter good deed description: ")

    # Ensure required fields are not empty
    if not user_id or not description:
        print("Error: Both user ID and description are required.")
        return

    good_deed = {
        "user_id": user_id,
        "title": title,
        "location": {
            "city": city,
            "state": state,
            "country": country,
            "coordinates": {"latitude": latitude, "longitude": longitude}
        },
        "description": description,
        "completed_at": datetime.utcnow(),
        "streak_continued": bool(input("Streak continued (True/False): ")),
        "replies": []
    }

    try:
        result = good_deeds.insert_one(good_deed)
        print(f"Good deed added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the good deed: {e}")


# # Add a new user with validation for required fields and default values
def add_user():
    name = input("Enter user name: ")
    email = input("Enter email: ")
    # Validate email format using regex
        # Validate email format
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, email):
        print("Error: Invalid email format.")
        return
    city = input("Enter city: ")
    state = input("Enter state: ")
    country = input("Enter country: ")
    password = input("Enter password: ")

    # Ensure none of the required fields are empty
    if not name or not email or not city or not state or not country:
        print("Error: All fields (name, email, city, state, country) are required.")
        return

    # Set default values for optional fields
    streak = input("Enter streak count (leave blank for 0): ")
    streak = int(streak) if streak else 0  # Default streak to 0 if left blank
    mood = input("Enter mood: ")

    user = {
        "name": name,
        "email": email,
        "password": password, # Has to hashed 
        "location": {
            "city": city,
            "state": state,
            "country": country,
            "coordinates": {
                "latitude": float(input("Enter latitude: ")),
                "longitude": float(input("Enter longitude: "))
            }
        },
        "streak": streak,
        "mood": mood,
        "created_at": datetime.utcnow()
    }

    try:
        result = users.insert_one(user)
        print(f"User added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the user: {e}")



# # Add a news article with validation for required fields
# def add_news():
#     title = input("Enter news title: ")
#     content = input("Enter news content: ")
#     city = input("Enter city: ")
#     state = input("Enter state: ")
#     country = input("Enter country: ")

#     # Ensure required fields are not empty
#     if not title or not content or not city or not state or not country:
#         print("Error: All fields (title, content, city, state, country) are required.")
#         return

#     news_article = {
#         "title": title,
#         "content": content,
#         "location": {
#             "city": city,
#             "state": state,
#             "country": country
#         },
#         "sentiment": "positive",
#         "published_at": datetime.utcnow(),
#         "source": input("Enter news source: ")
#     }

#     try:
#         result = news.insert_one(news_article)
#         print(f"News article added with ID: {result.inserted_id}")
#     except pymongo.errors.PyMongoError as e:
#         print(f"An error occurred while adding the news article: {e}")

# Add a news article with validation for required fields
def add_news():
    title = input("Enter news title: ")
    content = input("Enter news content: ")
    city = input("Enter city: ")
    state = input("Enter state: ")
    country = input("Enter country: ")

    # Ensure required fields are not empty
    if not title or not content or not city or not state or not country:
        print("Error: All fields (title, content, city, state, country) are required.")
        return

    # Ask user for coordinates
    latitude = input("Enter latitude (e.g., 40.7128): ")
    longitude = input("Enter longitude (e.g., -74.0060): ")

    # Ensure coordinates are not empty
    if not latitude or not longitude:
        print("Error: Both latitude and longitude are required.")
        return
    
     # Convert coordinates to floats and ensure they are valid
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        print("Error: Latitude and longitude must be valid numbers.")
        return

    news_article = {
        "title": title,
        "content": content,
        "location": {
            "city": city,
            "state": state,
            "country": country,
            "coordinates": {
                "latitude": latitude,    
                "longitude": longitude
            }
        },
        "sentiment": "positive",
        "published_at": datetime.utcnow(),
        "source": input("Enter news source: ")
    }

    try:
        result = news.insert_one(news_article)
        print(f"News article added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the news article: {e}")


# Add a reply with validation for required fields
def add_reply():
    deed_id = input("Enter good deed ID: ")
    user_id = input("Enter user ID: ")
    content = input("Enter reply content: ")

    # Ensure required fields are not empty
    if not deed_id or not user_id or not content:
        print("Error: Good deed ID, user ID, and content are required.")
        return

    reply = {
        "deed_id": deed_id,
        "user_id": user_id,
        "content": content,
        "created_at": datetime.utcnow()
    }

    try:
        result = replies.insert_one(reply)
        print(f"Reply added with ID: {result.inserted_id}")

        # Update the good deed with the reply ID
        good_deeds.update_one(
            {"_id": ObjectId(deed_id)},
            {"$push": {"replies": result.inserted_id}}
        )
        print("Reply added to the good deed successfully.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the reply: {e}")

# View all documents in a collection, with replies for GoodDeeds
def view_all(collection):
    try:
        documents = list(collection.find())  # Convert cursor to a list
        if len(documents) == 0:
            print(f"No documents found in {collection.name}.")
        else:
            for doc in documents:
                print(f"\nDocument ID: {doc['_id']}")
                for key, value in doc.items():
                    if key != "_id":
                        print(f"{key.capitalize()}: {value}")
                
                # If viewing good deeds, fetch and display replies
                if collection.name == "good_deeds" and 'replies' in doc:
                    print("\nReplies:")
                    if len(doc['replies']) == 0:
                        print("No replies for this good deed.")
                    else:
                        for reply_id in doc['replies']:
                            reply = replies.find_one({"_id": ObjectId(reply_id)})
                            if reply:
                                print(f"  Reply by User {reply['user_id']} on {reply['created_at']}:")
                                print(f"    {reply['content']}")
                            else:
                                print(f"  Reply with ID {reply_id} not found.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while retrieving documents from {collection.name}: {e}")
def view_replies():
    deed_id = input("Enter the ID of the good deed to view replies: ").strip()  # Strip whitespace

    try:
        # Find the good deed by its ID
        good_deed = good_deeds.find_one({"_id": ObjectId(deed_id)})
        
        if good_deed:
            print(f"\nGood Deed ID: {good_deed['_id']}")
            print(f"Title: {good_deed['title']}")
            print(f"Description: {good_deed['description']}")
            # print(f"Completed At: {good_deed['completed_at']}")
            print("Replies:")
            
            # Fetch replies based on the good deed's replies list
            if 'replies' in good_deed and good_deed['replies']:
                for reply_id in good_deed['replies']:
                    reply = replies.find_one({"_id": ObjectId(reply_id)})
                    if reply:
                        print(f"  Reply ID: {reply['_id']}")
                        print(f"  User ID: {reply['user_id']}")
                        print(f"  Content: {reply['content']}")
                        print(f"  Created At: {reply['created_at']}")
                    else:
                        print(f"  Reply with ID {reply_id} not found.")
            else:
                print("  No replies found for this good deed.")
        else:
            print(f"No good deed found with ID: {deed_id}")

    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while retrieving replies: {e}")



# Update a reply in the replies collection with valid field checks
def update_reply():
    reply_id = input("Enter the ID of the reply to update: ")
    field = input("Enter the field to update (content): ").lower()  # Normalize field name to lowercase
    value = input("Enter the new value: ")

    # Define valid fields for the replies collection
    valid_reply_fields = ['deed_id', 'user_id', 'content', 'created_at']

    # Check if the field is valid
    if field not in valid_reply_fields:
        print(f"Error: '{field}' is not a valid field in the 'replies' collection.")
        return

    # Handle type casting for specific fields
    if field == 'created_at':
        # Example format for datetime fields: '2024-10-06 12:00:00'
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    try:
        result = replies.update_one(
            {"_id": ObjectId(reply_id)},
            {"$set": {field: value}}
        )
        if result.modified_count:
            print("Reply updated successfully!")
        else:
            print("No reply found with that ID.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while updating the reply: {e}")
        
# Update a document in a collection with valid fields for each collection, and special handling for location
def update_document(collection):
    doc_id = input(f"Enter the ID of the document to update in {collection.name}: ")
    field = input("Enter the field to update: ").lower()  # Convert field to lowercase to prevent case mismatch

    # Define valid fields for each collection
    valid_fields = {
        "users": ['name', 'email', 'location', 'streak', 'mood', 'created_at'],
        "good_deeds": ['description', 'user_id', 'location', 'completed_at', 'streak_continued', 'replies'],
        "news": ['title', 'content', 'location', 'sentiment', 'published_at', 'source'],
        "replies": ['deed_id', 'user_id', 'content', 'created_at']
    }

    # Get the valid fields for the current collection
    collection_name = collection.name
    if collection_name not in valid_fields:
        print(f"Error: '{collection_name}' is not a recognized collection.")
        return

    # Check if the field is valid for the current collection
    if field not in valid_fields[collection_name]:
        print(f"Error: '{field}' is not a valid field in the '{collection_name}' collection.")
        return

    # Special case for updating location
    if field == "location":
        location_field = input("Do you want to update 'city', 'state', or 'country'? ").lower()
        if location_field not in ['city', 'state', 'country']:
            print("Error: Invalid location field. Please choose either 'city', 'state', or 'country'.")
            return
        
        value = input(f"Enter the new value for {location_field}: ")

        # Update the nested location field
        try:
            result = collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {f"location.{location_field}": value}}
            )
            if result.modified_count:
                print(f"Document's location ({location_field}) updated successfully!")
            else:
                print(f"No document found with that ID in {collection_name}.")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred while updating the location in {collection_name}: {e}")
        return  # Return early since location has been handled separately

    # Handle type casting for specific fields
    value = input("Enter the new value: ")  # Get value after handling location

    if field in ['latitude', 'longitude', 'streak']:
        value = float(value)
    elif field == 'streak_continued':
        value = bool(value)
    elif field == 'created_at' or field == 'completed_at' or field == 'published_at':
        # Example format for datetime fields: '2024-10-06 12:00:00'
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    # Standard update for other fields
    try:
        result = collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {field: value}}
        )
        if result.modified_count:
            print(f"Document in {collection_name} updated successfully!")
        else:
            print(f"No document found with that ID in {collection_name}.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while updating the document in {collection_name}: {e}")


# Delete a reply and remove its reference from the good deed
def delete_reply():
    reply_id = input("Enter the ID of the reply to delete: ")
    
    try:
        # First, remove the reply from the replies collection
        result = replies.delete_one({"_id": ObjectId(reply_id)})

        if result.deleted_count:
            print("Reply deleted successfully from replies collection!")
            
            # Also, remove the reference to this reply from the corresponding good deed
            good_deeds.update_one(
                {"replies": ObjectId(reply_id)},
                {"$pull": {"replies": ObjectId(reply_id)}}
            )
            print("Reply reference removed from the associated good deed!")
        else:
            print("No reply found with that ID.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while deleting the reply: {e}")


# Delete a document in a collection
def delete_document(collection):
    doc_id = input(f"Enter the ID of the document to delete in {collection.name}: ")

    try:
        result = collection.delete_one({"_id": ObjectId(doc_id)})
        if result.deleted_count:
            print(f"Document deleted successfully from {collection.name}!")
        else:
            print(f"No document found with that ID in {collection.name}.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while deleting the document from {collection.name}: {e}")

# Main function to display menu
def main():
    while True:
        print("\nHappyNest Application")
        print("1. Add a user")
        print("2. Add a good deed")
        print("3. Add a news article")
        print("4. Add a reply to a good deed")
        print("5. View all users")
        print("6. View all good deeds")
        print("7. View all news articles")
        print("8. View all replies")  # New option added
        print("9. Update a user")
        print("10. Update a good deed")
        print("11. Update a news article")
        print("12. Update a reply")
        print("13. Delete a user")
        print("14. Delete a good deed")
        print("15. Delete a news article")
        print("16. Delete a reply")
        print("17. Exit")  # Updated option number

        choice = input("Enter your choice (1-17): ")  # Updated range

        if choice == '1':
            add_user()
        elif choice == '2':
            add_good_deed()
        elif choice == '3':
            add_news()
        elif choice == '4':
            add_reply()
        elif choice == '5':
            view_all(users)
        elif choice == '6':
            view_all(good_deeds)
        elif choice == '7':
            view_all(news)
        elif choice == '8':  
            view_replies() 
        elif choice == '9':
            update_document(users)
        elif choice == '10':
            update_document(good_deeds)
        elif choice == '11':
            update_document(news)
        elif choice == '12':
            update_reply()
        elif choice == '13':
            delete_document(users)
        elif choice == '14':
            delete_document(good_deeds)
        elif choice == '15':
            delete_document(news)
        elif choice == '16':
            delete_reply()
        elif choice == '17':  
            break
        else:
            print("Invalid choice. Please try again.")

    client.close()
    print("Goodbye!")

def add_sample_users():
    """Function to insert sample users into the MongoDB collection."""
    users_sample = [
        {"name": "Alice Johnson", "email": "alice.j@example.com", "password": "hashed_password", 
         "location": {"city": "New York", "state": "NY", "country": "USA", 
                      "coordinates": {"latitude": 40.7128, "longitude": -74.0060}}, 
         "streak": 5, "mood": "Happy", "created_at": datetime.utcnow()},
        {"name": "Bob Smith", "email": "bob.s@example.com", "password": "hashed_password", 
         "location": {"city": "Los Angeles", "state": "CA", "country": "USA", 
                      "coordinates": {"latitude": 34.0522, "longitude": -118.2437}}, 
         "streak": 2, "mood": "Excited", "created_at": datetime.utcnow()},
        {"name": "Carlos Martinez", "email": "carlos.m@example.com", "password": "hashed_password", 
         "location": {"city": "Miami", "state": "FL", "country": "USA", 
                      "coordinates": {"latitude": 25.7617, "longitude": -80.1918}}, 
         "streak": 8, "mood": "Cheerful", "created_at": datetime.utcnow()},
        {"name": "Diana Cheng", "email": "diana.c@example.com", "password": "hashed_password", 
         "location": {"city": "San Francisco", "state": "CA", "country": "USA", 
                      "coordinates": {"latitude": 37.7749, "longitude": -122.4194}}, 
         "streak": 3, "mood": "Motivated", "created_at": datetime.utcnow()},
        {"name": "Edward King", "email": "edward.k@example.com", "password": "hashed_password", 
         "location": {"city": "Chicago", "state": "IL", "country": "USA", 
                      "coordinates": {"latitude": 41.8781, "longitude": -87.6298}}, 
         "streak": 10, "mood": "Grateful", "created_at": datetime.utcnow()},
        {"name": "Fiona Davis", "email": "fiona.d@example.com", "password": "hashed_password", 
         "location": {"city": "Boston", "state": "MA", "country": "USA", 
                      "coordinates": {"latitude": 42.3601, "longitude": -71.0589}}, 
         "streak": 6, "mood": "Joyful", "created_at": datetime.utcnow()},
        {"name": "George Williams", "email": "george.w@example.com", "password": "hashed_password", 
         "location": {"city": "Austin", "state": "TX", "country": "USA", 
                      "coordinates": {"latitude": 30.2672, "longitude": -97.7431}}, 
         "streak": 4, "mood": "Optimistic", "created_at": datetime.utcnow()},
        {"name": "Hannah Lee", "email": "hannah.l@example.com", "password": "hashed_password", 
         "location": {"city": "Seattle", "state": "WA", "country": "USA", 
                      "coordinates": {"latitude": 47.6062, "longitude": -122.3321}}, 
         "streak": 1, "mood": "Calm", "created_at": datetime.utcnow()},
        {"name": "Ian O'Reilly", "email": "ian.o@example.com", "password": "hashed_password", 
         "location": {"city": "Orlando", "state": "FL", "country": "USA", 
                      "coordinates": {"latitude": 28.5383, "longitude": -81.3792}}, 
         "streak": 7, "mood": "Content", "created_at": datetime.utcnow()},
        {"name": "Julia Adams", "email": "julia.a@example.com", "password": "hashed_password", 
         "location": {"city": "Denver", "state": "CO", "country": "USA", 
                      "coordinates": {"latitude": 39.7392, "longitude": -104.9903}}, 
         "streak": 0, "mood": "Hopeful", "created_at": datetime.utcnow()}
    ]

    try:
        # Insert multiple users at once into the 'users' collection
        result = users.insert_many(users_sample)
        print(f"Inserted {len(result.inserted_ids)} sample users.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding sample users: {e}")




def random_date(start, end):
    """Generate a random datetime between two datetime objects."""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randint(0, int_delta)
    return start + timedelta(seconds=random_second)

def add_sample_news():
    """Function to insert sample news articles into the MongoDB collection."""
    news_sample = [
        {
            "title": "Community Garden Thrives",
            "content": "A local community garden has been flourishing thanks to volunteers.", 
            "location": {
                "city": "New York", 
                "state": "NY", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 40.7128,    
                    "longitude": -74.0060
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Park Clean-up Day Successful",
            "content": "Over 100 volunteers helped clean the park this weekend.", 
            "location": {
                "city": "Los Angeles", 
                "state": "CA", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 34.0522,    
                    "longitude": -118.2437
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Charity Drive Exceeds Goals",
            "content": "The charity drive collected over $10,000 for local families.", 
            "location": {
                "city": "Miami", 
                "state": "FL", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 25.7617,    
                    "longitude": -80.1918
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Animal Shelter Receives Donations",
            "content": "The shelter received a generous donation from the community.", 
            "location": {
                "city": "San Francisco", 
                "state": "CA", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 37.7749,    
                    "longitude": -122.4194
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Local Soup Kitchen Opens New Branch",
            "content": "A new branch of the soup kitchen has opened downtown.", 
            "location": {
                "city": "Chicago", 
                "state": "IL", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 41.8781,    
                    "longitude": -87.6298
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "After-School Program Helps Kids",
            "content": "An after-school program is providing support for children in need.", 
            "location": {
                "city": "Boston", 
                "state": "MA", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 42.3601,    
                    "longitude": -71.0589
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Environmental Awareness Day Held",
            "content": "The community came together for environmental awareness.", 
            "location": {
                "city": "Austin", 
                "state": "TX", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 30.2672,    
                    "longitude": -97.7431
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Fundraiser for Local Library",
            "content": "A successful fundraiser has raised money for the local library.", 
            "location": {
                "city": "Seattle", 
                "state": "WA", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 47.6062,    
                    "longitude": -122.3321
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Blood Donation Event a Success",
            "content": "A blood donation event gathered many donors.", 
            "location": {
                "city": "Orlando", 
                "state": "FL", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 28.5383,    
                    "longitude": -81.3792
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        },
        {
            "title": "Community Sports Day Announced",
            "content": "A sports day event will be held to promote community engagement.", 
            "location": {
                "city": "Denver", 
                "state": "CO", 
                "country": "USA", 
                "coordinates": {
                    "latitude": 39.7392,    
                    "longitude": -104.9903
                }
            }, 
            "sentiment": "positive",
            "published_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1))
        }
    ]

    try:
        # Insert multiple news articles at once into the 'news' collection
        result = news.insert_many(news_sample)
        print(f"Inserted {len(result.inserted_ids)} sample news articles.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding sample news articles: {e}")


def delete_all_good_deeds():
    confirmation = input("Are you sure you want to delete ALL good deeds? This action cannot be undone. (yes/no): ").strip().lower()
    
    if confirmation == 'yes':
        try:
            result = good_deeds.delete_many({})  # Delete all documents
            print(f"Deleted {result.deleted_count} good deed(s) from the collection.")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred while deleting good deeds: {e}")
    else:
        print("Operation cancelled. No good deeds were deleted.")
def delete_all_sample_news():
    """Function to delete all sample news from the MongoDB collection."""
    try:
        # Delete all documents from the 'news' collection
        result = news.delete_many({})
        print(f"Deleted {result.deleted_count} sample news entries.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while deleting sample news: {e}")
def delete_all_replies():
    try:
        # Delete all documents in the 'replies' collection
        result = replies.delete_many({})
        print(f"Deleted {result.deleted_count} replies.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while deleting replies: {e}")
def add_sample_good_deeds():
    """Function to insert sample good deeds into the MongoDB collection."""
    good_deeds_sample = [
        {
            "user_id": "user1",
            "title": "Helped a neighbor with groceries",
            "location": {
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "coordinates": {"latitude": 40.7128, "longitude": -74.0060}
            },
            "description": "Assisted Mrs. Thompson in carrying her groceries.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        },
        {
            "user_id": "user2",
            "title": "Organized a community clean-up",
            "location": {
                "city": "Los Angeles",
                "state": "CA",
                "country": "USA",
                "coordinates": {"latitude": 34.0522, "longitude": -118.2437}
            },
            "description": "Led a team to clean up the local park.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": False,
            "replies": []
        },
        {
            "user_id": "user3",
            "title": "Donated clothes to charity",
            "location": {
                "city": "Miami",
                "state": "FL",
                "country": "USA",
                "coordinates": {"latitude": 25.7617, "longitude": -80.1918}
            },
            "description": "Donated winter clothes to the homeless shelter.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        },
        {
            "user_id": "user4",
            "title": "Volunteered at the animal shelter",
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
                "coordinates": {"latitude": 37.7749, "longitude": -122.4194}
            },
            "description": "Spent time caring for animals at the shelter.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        },
        {
            "user_id": "user5",
            "title": "Cooked meals for the needy",
            "location": {
                "city": "Chicago",
                "state": "IL",
                "country": "USA",
                "coordinates": {"latitude": 41.8781, "longitude": -87.6298}
            },
            "description": "Prepared and served meals at the local soup kitchen.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": False,
            "replies": []
        },
        {
            "user_id": "user6",
            "title": "Tutored children in math",
            "location": {
                "city": "Boston",
                "state": "MA",
                "country": "USA",
                "coordinates": {"latitude": 42.3601, "longitude": -71.0589}
            },
            "description": "Helped local kids improve their math skills.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        },
        {
            "user_id": "user7",
            "title": "Planted trees in the community",
            "location": {
                "city": "Austin",
                "state": "TX",
                "country": "USA",
                "coordinates": {"latitude": 30.2672, "longitude": -97.7431}
            },
            "description": "Participated in a tree-planting event.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": False,
            "replies": []
        },
        {
            "user_id": "user8",
            "title": "Spearheaded a fundraiser",
            "location": {
                "city": "Seattle",
                "state": "WA",
                "country": "USA",
                "coordinates": {"latitude": 47.6062, "longitude": -122.3321}
            },
            "description": "Organized a fundraiser to support local charities.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        },
        {
            "user_id": "user9",
            "title": "Conducted a blood drive",
            "location": {
                "city": "Orlando",
                "state": "FL",
                "country": "USA",
                "coordinates": {"latitude": 28.5383, "longitude": -81.3792}
            },
            "description": "Organized a blood donation event.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": False,
            "replies": []
        },
        {
            "user_id": "user10",
            "title": "Visited the elderly in nursing homes",
            "location": {
                "city": "Denver",
                "state": "CO",
                "country": "USA",
                "coordinates": {"latitude": 39.7392, "longitude": -104.9903}
            },
            "description": "Spent time with residents at a local nursing home.",
            "completed_at": random_date(datetime(2023, 1, 1), datetime(2024, 1, 1)),
            "streak_continued": True,
            "replies": []
        }
    ]

    try:
        # Insert multiple good deeds at once into the 'good_deeds' collection
        result = good_deeds.insert_many(good_deeds_sample)
        print(f"Inserted {len(result.inserted_ids)} sample good deeds.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding sample good deeds: {e}")
def add_sample_replies():
    """Function to insert sample replies into the MongoDB collection with random created_at timestamps."""
    sample_replies = [
        {
            "deed_id": "670db9029d6bb3955fe433b4",  # ID of the good deed
            "user_id": "user2",
            "content": "That's wonderful! Helping neighbors is so important.",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b4",  # ID of the good deed
            "user_id": "user3",
            "content": "Great job! Every bit counts.",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b5",  # ID of the good deed
            "user_id": "user1",
            "content": "This is inspiring! Thank you for organizing!",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b6",  # ID of the good deed
            "user_id": "user4",
            "content": "So generous! Your contribution makes a difference.",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b7",  # ID of the good deed
            "user_id": "user5",
            "content": "Animals need love too! Thank you for your work!",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b8",  # ID of the good deed
            "user_id": "user6",
            "content": "Fundraisers like these are essential! Well done!",
        },
        {
            "deed_id": "670db9029d6bb3955fe433b9",  # ID of the good deed
            "user_id": "user7",
            "content": "Blood drives save lives! Kudos for organizing!",
        },
        {
            "deed_id": "670db9029d6bb3955fe433ba",  # ID of the good deed
            "user_id": "user8",
            "content": "Your time spent with the elderly is so valuable!",
        }
    ]

    try:
        replies_to_insert = []
        for reply in sample_replies:
            # Fetch the completed_at timestamp for the corresponding good deed
            good_deed = good_deeds.find_one({"_id": ObjectId(reply["deed_id"])})
            if good_deed and "completed_at" in good_deed:
                # Create a random time after the good deed's completed_at
                completed_at = good_deed["completed_at"]
                # Generate a random timedelta between 1 minute and 10 days
                random_time_delta = random.randint(1, 10 * 24 * 60)  # minutes
                created_at = completed_at + timedelta(minutes=random_time_delta)

                replies_to_insert.append({
                    "deed_id": reply["deed_id"],
                    "user_id": reply["user_id"],
                    "content": reply["content"],
                    "created_at": created_at
                })

        # Insert multiple replies at once into the 'replies' collection
        result = replies.insert_many(replies_to_insert)
        print(f"Inserted {len(result.inserted_ids)} sample replies.")

        # Update the good deeds with the new reply IDs
        for reply_id, reply in zip(result.inserted_ids, replies_to_insert):
            good_deeds.update_one(
                {"_id": ObjectId(reply["deed_id"])},
                {"$push": {"replies": reply_id}}
            )
        print("All replies added to their respective good deeds successfully.")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding sample replies: {e}")

if __name__ == "__main__":
    # add_sample_users()
    # add_sample_good_deeds()
        
    # # Retrieve the IDs of the inserted good deeds to use for replies
    # delete_all_sample_news()
    # add_sample_news()
    # delete_all_good_deeds()
    # delete_all_replies()

    # add_sample_replies()
    main()
