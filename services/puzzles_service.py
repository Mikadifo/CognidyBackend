from google import genai
from config.env_config import get_env_config
from database import get_puzzles_collection, get_users_collection
from constants.collections import Collection
import json
from datetime import datetime

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

#CRUD operations for guest puzzles

def delete_guest_puzzle(puzzle_id):
    puzzles_collection = get_puzzles_collection()
    result = puzzles_collection.delete_one({"puzzle_id": puzzle_id})
    return result.deleted_count > 0

def update_guest_puzzle_completion(puzzle_id, completed):
    #1. find the puzzle from the db (by puzzle_id, will be the most recent state that was last saved)
    #2. update its 'completed' field to True if completed, AnswerGrid with all the letters in places where the user placed them

    puzzles_collection = get_puzzles_collection()
    result = puzzles_collection.find_one_and_update(
        {"puzzle_id": puzzle_id},
        {"$set": {"completed": str(completed)}},
        return_document=True
    )
      #something where the result is the updated document, maybe I make a copy 
    return result

def return_guest_puzzle(puzzle_id):
    puzzles_collection = get_puzzles_collection()
    puzzle = puzzles_collection.find_one({"puzzle_id": puzzle_id})
    if puzzle is None:
        print("No puzzle found with the given puzzle_id.")
        return None
    else:
        return puzzle
    
def generate_guest_puzzle(file):
    if file is None:
        return "No file provided."
    try:
        #here, set the puzzle id to be the date and time it was created
        puzzle_id = datetime.now().strftime("%Y%m%d%H%M%S")

        genai_file = genai_client.files.upload(file=file)

        prompt = """
        Based on the content of the uploaded file, generate a crossword puzzle in JSON format for a Next.js frontend.
        
        Requirements:
        1. Extract 8-12 key terms from the file content
        2. Create two 30x30 crossword grids, one should contain all of the correct letters filled in, and the other should be empty
        3. Use null for empty cells, letters for filled cells, and numbers for word starts
        4. Ensure words intersect logically, sharing letters where applicable for a valid crossword puzzle
        
        for your understanding:
        the filled grid is the answer key, while the empty grid is what the user will see and fill in.

        Return ONLY valid JSON with this exact structure:
        {
          "metadata": {
            "puzzleID": "puzzle_id",
            "title": "Generated from [filename]",
            "completed": false
          },
          "AnswerGrid": {[
            // 30x30 array where null = empty cell, letters for filled cells
          ],
          "UserGrid": [
            // 30x30 array where null = empty cell
          ],
          "words": [
            {
              "word": "EXAMPLE", "direction": across|down, "number": 1
              "word": "NEWLINE", "direction", across|down, "number": 2
          ],
        }

        here is an example puzzle to follow, albeit with a 6x6 grid for simplicity
        (they're spaced out here for readability, but should be continuous arrays in actual JSON, so 6 rows of 6 elements each for this example):
        {
  "metadata": {
    "puzzleID": "puzzle_id",
    "title": "Generated from sample.txt",
    "completed": false
  },

  "answerGrid": [
    ["C",  "A",  "T",  null, null, null],
    [null, null, "A",  null, null, null],
    [null, null, "R",  "A",  "T",  null],
    [null, null, null, "R",  null, null],
    [null, null, null, "T",  null, null],
    [null, null, null, null, null, null]
  ],

  "userGrid": [
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null]
  ],

  "words": [
    {
      "number": 1,
      "word": "CAT",
      "direction": "across",
      "startRow": 0,
      "startCol": 0,
      "length": 3,
      "hint": "A small domesticated feline."
    },
    {
      "number": 2,
      "word": "TAR",
      "direction": "down",
      "startRow": 2,
      "startCol": 0,
      "length": 3,
      "hint": "A black viscous material used on roads."
    },
    {
      "number": 3,
      "word": "RAT",
      "direction": "across",
      "startRow": 2,
      "startCol": 2,
      "length": 3,
      "hint": "A rodent resembling a large mouse."
    },
    {
      "number": 4,
      "word": "ART",
      "direction": "down",
      "startRow": 3,
      "startCol": 2,
      "length": 3,
      "hint": "Human creative expression."
    }
  ]
}

        """

        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, genai_file]
        )

        if genai_file.name is not None:
            genai_client.files.delete(name=genai_file.name)

        # Parse the AI response
        try:
            puzzle_data = json.loads(response.text)
        except json.JSONDecodeError:
            print("Failed to parse AI response as JSON")
            return None

        try:
            #save to database
            puzzles_collection = get_puzzles_collection()
            puzzle_document = {
                "metadata": puzzle_data.get("metadata", {}),
                "AnswerGrid": puzzle_data.get("AnswerGrid", []),
                "UserGrid": puzzle_data.get("UserGrid", []),
                "words": puzzle_data.get("words", []),
            }
            result = puzzles_collection.insert_one(puzzle_document)
            puzzle_document["_id"] = str(result.inserted_id)
            return puzzle_document
        except Exception as db_error:
            print(f"Error saving puzzle to database: {db_error}")
    except:
        return "Error! Backtrack with debugger."

def generate_user_puzzles(file, user_id):
    if file is None:
        return "No file provided."
    
    if user_id is None:
        return "No user ID provided, please provide a valid user ID."
    try:
        
        #here, set the puzzle id to be the date and time it was created
        puzzle_id = datetime.now().strftime("%Y%m%d%H%M%S")


        genai_file = genai_client.files.upload(file=file)

        prompt = """
        Based on the content of the uploaded file, generate a crossword puzzle in JSON format for a Next.js frontend.
        
        Requirements:
        1. Extract 8-12 key terms from the file content
        2. Create two 30x30 crossword grids, one should contain all of the correct letters filled in, and the other should be empty
        3. Use null for empty cells, letters for filled cells, and numbers for word starts
        4. Ensure words intersect logically, sharing letters where applicable for a valid crossword puzzle
        
        for your understanding:
        the filled grid is the answer key, while the empty grid is what the user will see and fill in.

        Return ONLY valid JSON with this exact structure:
        {
          "metadata": {
            "puzzleID": "puzzle_id",
            "userID": "user_id",
            "title": "Generated from [filename]",
            "completed": false
          },
          "AnswerGrid": {[
            // 30x30 array where null = empty cell, letters for filled cells
          ],
          "UserGrid": [
            // 30x30 array where null = empty cell
          ],
          "words": [
            {
              "word": "EXAMPLE", "direction": across|down, "number": 1
              "word": "NEWLINE", "direction", across|down, "number": 2
          ],
        }

        here is an example puzzle to follow, albeit with a 6x6 grid for simplicity
        (they're spaced out here for readability, but should be continuous arrays in actual JSON, so 6 rows of 6 elements each for this example):
        {
  "metadata": {
    "puzzleID": "puzzle_id",
    "userID": "user_id",
    "title": "Generated from sample.txt",
    "completed": false
  },

  "answerGrid": [
    ["C",  "A",  "T",  null, null, null],
    [null, null, "A",  null, null, null],
    [null, null, "R",  "A",  "T",  null],
    [null, null, null, "R",  null, null],
    [null, null, null, "T",  null, null],
    [null, null, null, null, null, null]
  ],

  "userGrid": [
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null],
    [null, null, null, null, null, null]
  ],

  "words": [
    {
      "number": 1,
      "word": "CAT",
      "direction": "across",
      "startRow": 0,
      "startCol": 0,
      "length": 3,
      "hint": "A small domesticated feline."
    },
    {
      "number": 2,
      "word": "TAR",
      "direction": "down",
      "startRow": 2,
      "startCol": 0,
      "length": 3,
      "hint": "A black viscous material used on roads."
    },
    {
      "number": 3,
      "word": "RAT",
      "direction": "across",
      "startRow": 2,
      "startCol": 2,
      "length": 3,
      "hint": "A rodent resembling a large mouse."
    },
    {
      "number": 4,
      "word": "ART",
      "direction": "down",
      "startRow": 3,
      "startCol": 2,
      "length": 3,
      "hint": "Human creative expression."
    }
  ]
}

        """

        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, genai_file]
        )

        if genai_file.name is not None:
            genai_client.files.delete(name=genai_file.name)

        # Parse the AI response
        try:
            puzzle_data = json.loads(response.text)
        except json.JSONDecodeError:
            print("Failed to parse AI response as JSON")
            return None

        try:
            #save to database
            puzzles_collection = get_puzzles_collection()
            puzzle_document = {
                "metadata": puzzle_data.get("metadata", {}),
                "AnswerGrid": puzzle_data.get("AnswerGrid", []),
                "UserGrid": puzzle_data.get("UserGrid", []),
                "words": puzzle_data.get("words", []),
            }
            result = puzzles_collection.insert_one(puzzle_document)
            puzzle_document["_id"] = str(result.inserted_id)
            return puzzle_document
        except Exception as db_error:
            print(f"Error saving puzzle to database: {db_error}")
    except:
        return "Error! Backtrack with debugger."