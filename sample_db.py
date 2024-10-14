import os
from dotenv import load_dotenv
import pymongo
import re
from bson.objectid import ObjectId
from datetime import datetime

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
# def add_user():
#     name = input("Enter user name: ")
#     email = input("Enter email: ")
#     # Validate email format using regex
#         # Validate email format
#     email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#     if not re.match(email_pattern, email):
#         print("Error: Invalid email format.")
#         return
#     city = input("Enter city: ")
#     state = input("Enter state: ")
#     country = input("Enter country: ")
#     password = input("Enter password: ")

#     # Ensure none of the required fields are empty
#     if not name or not email or not city or not state or not country:
#         print("Error: All fields (name, email, city, state, country) are required.")
#         return

#     # Set default values for optional fields
#     streak = input("Enter streak count (leave blank for 0): ")
#     streak = int(streak) if streak else 0  # Default streak to 0 if left blank
#     mood = input("Enter mood: ")

#     user = {
#         "name": name,
#         "email": email,
#         "password": password, # Has to hashed 
#         "location": {
#             "city": city,
#             "state": state,
#             "country": country,
#             "coordinates": {
#                 "latitude": float(input("Enter latitude: ")),
#                 "longitude": float(input("Enter longitude: "))
#             }
#         },
#         "streak": streak,
#         "mood": mood,
#         "created_at": datetime.utcnow()
#     }

#     try:
#         result = users.insert_one(user)
#         print(f"User added with ID: {result.inserted_id}")
#     except pymongo.errors.PyMongoError as e:
#         print(f"An error occurred while adding the user: {e}")


# # Add a good deed with validation for required fields
# def add_good_deed():
#     user_id = input("Enter user ID: ")
#     title = input("Enter good deed title: ")
#     city = input("Enter city: ")
#     state = input("Enter state: ")
#     country = input("Enter country: ")
#     description = input("Enter good deed description: ")

#     # Ensure required fields are not empty
#     if not user_id or not description:
#         print("Error: Both user ID and description are required.")
#         return

#     good_deed = {
#         "user_id": user_id,
#         "title": title,
#         "location": {
#             "city": city,
#             "state": state,
#             "country": country
#         },
#         "description": description,
#         "completed_at": datetime.utcnow(),
#         "streak_continued": bool(input("Streak continued (True/False): ")),
#         "replies": []
#     }

#     try:
#         result = good_deeds.insert_one(good_deed)
#         print(f"Good deed added with ID: {result.inserted_id}")
#     except pymongo.errors.PyMongoError as e:
#         print(f"An error occurred while adding the good deed: {e}")


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
        print("8. Update a user")
        print("9. Update a good deed")
        print("10. Update a news article")
        print("11. Update a reply")
        print("12. Delete a user")
        print("13. Delete a good deed")
        print("14. Delete a news article")
        print("15. Delete a reply")
        print("16. Exit")

        choice = input("Enter your choice (1-16): ")

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
            update_document(users)
        elif choice == '9':
            update_document(good_deeds)
        elif choice == '10':
            update_document(news)
        elif choice == '11':
            update_reply()
        elif choice == '12':
            delete_document(users)
        elif choice == '13':
            delete_document(good_deeds)
        elif choice == '14':
            delete_document(news)
        elif choice == '15':
            delete_reply()
        elif choice == '16':
            break
        else:
            print("Invalid choice. Please try again.")

    client.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()