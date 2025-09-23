#database connection and collection retrieval

from pymongo import MongoClient
from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()

#setting up database connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

#creating database instance
db = client[os.getenv("DB_NAME")]

#creation of collections using environment variables
userCollection = db[os.getenv("U_COL")]
thesaurusCollection = db[os.getenv("T_COL")]

def get_db():
    return db

def get_users_collection():
    return userCollection

def get_thesaurus_collection():
    return thesaurusCollection