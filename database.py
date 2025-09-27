# database connection and collection retrieval

from pymongo import MongoClient
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

# setting up database connection, assertion of environment variables to ensure the database can be accessed
DB_USERNAME = os.getenv("DB_USERNAME")
assert (
    DB_USERNAME is not None and len(DB_USERNAME) > 0
), "DB_USERNAME environment variable does not exist, or is empty"

DB_PASSWORD = os.getenv("DB_PASSWORD")
assert (
    DB_PASSWORD is not None and len(DB_PASSWORD) > 0
), "DB_PASSWORD environment variable does not exist, or is empty"

DB_NAME = os.getenv("DB_NAME")
assert (
    DB_NAME is not None and len(DB_NAME) > 0
), "DB_NAME environment variable does not exist, or is empty"

uri = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cognidy-cluster.oq1fqvx.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&appName=cognidy-cluster"
client = MongoClient(uri)

# creating database instance
db = client[DB_NAME]

# retrieval and assertion of collection names from environment variables
t_collection = os.getenv("T_COL")
assert (
    t_collection is not None and len(t_collection) > 0
), "T_COL environment variable does not exist, or is empty"

userCollection = db["users"]
thesaurusCollection = db[t_collection]


def get_db():
    return db


def get_users_collection():
    return userCollection


def get_thesaurus_collection():
    return thesaurusCollection

