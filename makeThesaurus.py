import wn
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import defaultdict
import os

# Load environment variables from .env file
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

# retrieval and assertion of thesaurusCollection name from environment variables
t_collection = os.getenv("T_COL")
assert (
    t_collection is not None and len(t_collection) > 0
), "T_COL environment variable does not exist, or is empty"

thesaurusCollection = db[t_collection]

# Download OEWN if not already downloaded
print("Downloading OEWN 2024...")
try:
    wn.download('oewn:2024')
except:
    print("OEWN already downloaded or download failed")

# Load OEWN
print("Loading OEWN...")
en = wn.Wordnet('oewn:2024')

print("Building word structures...")

# Dictionary to group synsets by word
word_data = defaultdict(list)

# Get all synsets and organize by word
for synset in en.synsets():
    definition = synset.definition()
    
    # Get synonyms (lemmas) for this synset
    synonyms = [lemma for lemma in synset.lemmas() if lemma]
    
    # Add this meaning to each word in the synset
    for word in synset.lemmas():
        word_data[word].append({
            'definition': definition,
            'synonyms': synonyms
        })

print(f"Processing {len(word_data)} unique words...")

# Prepare documents for batch insert
batch = []
batch_size = 1000
total_inserted = 0

for word, meanings in word_data.items():
    # Take only first 3 meanings
    limited_meanings = meanings[:3]
    
    document = {
        '_id': word,  # Use word as the unique identifier
        'word': word,
        'meanings': limited_meanings,
        'total_meanings': len(meanings)  # Keep track of how many meanings exist
    }
    
    batch.append(document)
    
    # Insert batch when it reaches batch_size
    if len(batch) >= batch_size:
        try:
            thesaurusCollection.insert_many(batch, ordered=False)
            total_inserted += len(batch)
            print(f"Inserted {total_inserted} words...")
            batch = []
        except Exception as e:
            print(f"Error inserting batch: {e}")
            batch = []

# Insert remaining documents
if batch:
    try:
        thesaurusCollection.insert_many(batch, ordered=False)
        total_inserted += len(batch)
        print(f"Inserted {total_inserted} words...")
    except Exception as e:
        print(f"Error inserting final batch: {e}")

print(f"\n✓ Migration complete!")
print(f"Total words inserted: {total_inserted}")

# Create index for faster queries
print("\nCreating index on 'word' field...")
thesaurusCollection.create_index('word')

# Show some statistics
print("\n--- Database Statistics ---")
print(f"Total documents: {thesaurusCollection.count_documents({})}")

# Show example document
print("\n--- Example Document ---")
example = thesaurusCollection.find_one({'word': 'dog'})
if example:
    print(f"Word: {example['word']}")
    print(f"Total meanings in OEWN: {example['total_meanings']}")
    print(f"Stored meanings: {len(example['meanings'])}")
    for i, meaning in enumerate(example['meanings'], 1):
        print(f"\nMeaning {i}:")
        print(f"  Definition: {meaning['definition']}")
        print(f"  Synonyms: {', '.join(meaning['synonyms'][:5])}")


print("\n✓ Done!")
# Note: This script assumes you have a running MongoDB instance and the necessary environment variables set.