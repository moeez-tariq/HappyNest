# Final Project: Project in Programming and Data Science

Our Schema:
![mongo_schema](https://github.com/user-attachments/assets/a1b17148-6744-4d40-97aa-49692ad5f994)


# HappyNest Application

This is a MongoDB-based Python application using **PyMongo** for interacting with the following collections:
- `Users`
- `GoodDeeds`
- `News`
- `Replies`

## Features Overview

### 1. **MongoDB Connection:**
   - Connects to MongoDB using the connection URI provided in an `.env` file.
   - Lists available databases and connects to the `HappyNest` database.
   - Handles connection errors with proper error handling.

### 2. **Adding Data:**
   - **Users**:
     - Fields: `name`, `email`, `password`, `location` (with nested fields: `city`, `state`, `country`, `coordinates`), `streak` (default `0`), `mood`, `created_at`.
     - Validation:
       - Ensures no empty fields for `name`, `email`, `city`, `state`, and `country`.
       - Default values: 
         - `streak` defaults to 0 if not provided.
       - `password` must be hashed (though in this example, we store it as plain text, hashing must be implemented).
   - **Good Deeds**:
     - Fields: `user_id`, `title`, `location` (with nested fields: `city`, `state`, `country`), `description`, `completed_at`, `streak_continued`, `replies`.
     - Validation:
       - Ensures `user_id`, `description`, `title`, `city`, `state`, and `country` are provided.
       - Initializes the `replies` field as an empty list by default.
   - **News**:
     - Fields: `title`, `content`, `location` (with nested fields: `city`, `state`, `country`), `sentiment` (default `"positive"`), `published_at`, `source`, `tags`.
     - Validation:
       - Ensures no empty fields for `title`, `content`, `city`, `state`, and `country`.
       - Default values:
         - `sentiment` defaults to `"positive"`.
         - `tags` are optional.
   - **Replies**:
     - Fields: `deed_id`, `user_id`, `content`, `created_at`.
     - Validation:
       - Ensures `deed_id`, `user_id`, and `content` are provided.
       - Automatically updates the associated good deed's `replies` array to include the reply.

### 3. **Viewing Data:**
   - **View All** functionality for:
     - `Users`, `GoodDeeds`, `News`, and `Replies`.
   - Special handling for **Good Deeds**:
     - Shows associated replies for each good deed by retrieving them from the `Replies` collection using `reply_id`.

### 4. **Updating Data:**
   - **Update functionality** for:
     - `Users`, `GoodDeeds`, `News`, `Replies`.
   - **Location updates**:
     - If the user chooses to update the `location` field in any collection (e.g., Users or GoodDeeds), they are given the option to update only `city`, `state`, or `country`.
   - Valid fields are checked for each collection:
     - `Users`: `name`, `email`, `location`, `streak`, `mood`, `created_at`.
     - `Good Deeds`: `description`, `user_id`, `title`, `location`, `completed_at`, `streak_continued`, `replies`.
     - `News`: `title`, `content`, `location`, `sentiment`, `published_at`, `source`, `tags`.
     - `Replies`: `deed_id`, `user_id`, `content`, `created_at`.
   - Validation:
     - Field names are converted to lowercase to prevent case mismatch.
     - Checks if the field to be updated exists in the respective collection.
     - Handles type casting for fields like `latitude`, `longitude`, `streak`, and date fields (`created_at`, `completed_at`, etc.).

### 5. **Deleting Data:**
   - **Delete functionality** for:
     - `Users`, `GoodDeeds`, `News`, `Replies`.
   - Special handling for **Replies**:
     - When a reply is deleted, it also removes the reference to that reply from the associated good deed's `replies` array.
   
### 6. **Data Integrity:**
   - All critical fields are validated before any insertions or updates are made to ensure that:
     - Required fields are not left empty.
     - Valid fields are always updated (no invalid fields can be inserted).
     - Location updates are granular, allowing specific updates to `city`, `state`, or `country`.

### 7. **General Error Handling:**
   - Handles errors from MongoDB using `PyMongoError` exceptions and provides descriptive error messages in case of failure during any database operation.

---

## How to Use

### Prerequisites:
- Install required Python libraries:
  ```bash
  pip install requirements.txt
  ```

### MongoDB Setup:
- Ensure MongoDB is running, either locally or on a cloud service like MongoDB Atlas.
- Store your MongoDB URI in an `.env` file with the following content:
  ```
  MONGODB_URI=mongodb+srv://<your_mongo_uri>
  ```

### Running the Application:
- Run the main program:
  ```bash
  python <your_script_name>.py
  ```
- Follow the menu options to:
  - Add users, good deeds, news articles, and replies.
  - View all data from the collections.
  - Update and delete documents.
