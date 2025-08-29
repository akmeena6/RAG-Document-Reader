import os

import bcrypt
import pymongo
from pymongo.errors import ConnectionFailure

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["rag_users"]
    users_collection = db["users"]
    client.admin.command("ping")
    print("Successfully connected to MongoDB!")
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
    client = None


def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_user(username, password):
    """Inserts a new user into the database."""
    if users_collection.find_one({"username": username}):
        return False, "Username already exists."

    hashed_password = hash_password(password)
    user_document = {"username": username, "password": hashed_password}
    users_collection.insert_one(user_document)
    return True, "User created successfully."


def verify_user(username, password):
    """Verifies user credentials."""
    user = users_collection.find_one({"username": username})
    if user:
        # Verify the password
        return bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        )
    return False
