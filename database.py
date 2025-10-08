# database connection and collection retrieval

from pymongo import MongoClient

from config.env_config import get_env_config

env = get_env_config()

# setting up database connection, assertion of environment variables to ensure the database can be accessed
uri = f"mongodb+srv://{env.DB_USERNAME}:{env.DB_PASSWORD}@cognidy-cluster.oq1fqvx.mongodb.net/{env.DB_NAME}?retryWrites=true&w=majority&appName=cognidy-cluster"
client = MongoClient(uri)

# creating database instance
db = client[env.DB_NAME]

userCollection = db["users"]
thesaurusCollection = db["thesaurus"]
flashcardsCollection = db["flashcards"]
puzzlesCollection = db["puzzles"]
roadmapGoalsCollection = db["roadmap_goals"]


def get_db():
    return db

def get_users_collection():
    return userCollection

def get_thesaurus_collection():
    return thesaurusCollection

def get_puzzles_collection():
    return puzzlesCollection

def get_roadmap_goals_collection():
    return roadmapGoalsCollection
