# database connection and collection retrieval

from pymongo import MongoClient

from config.env_config import get_env_config
from constants.collections import Collection
import certifi


env = get_env_config()

# setting up database connection, assertion of environment variables to ensure the database can be accessed
uri = f"mongodb+srv://{env.DB_USERNAME}:{env.DB_PASSWORD}@cognidy-cluster.oq1fqvx.mongodb.net/{env.DB_NAME}?retryWrites=true&w=majority&appName=cognidy-cluster"
client = MongoClient(uri, tlsCAFile=certifi.where())

# creating database instance
db = client[env.DB_NAME]

def get_db():
    return db

def get_users_collection():
    return db[Collection.USERS.value]

def get_thesaurus_collection():
    return db[Collection.THESAURUS.value]

def get_flashcards_collection():
    return db[Collection.FLASHCARDS.value]

def get_puzzles_collection():
    return db[Collection.PUZZLES.value]

def get_roadmap_goals_collection():
    return db[Collection.ROADMAP_GOALS.value]