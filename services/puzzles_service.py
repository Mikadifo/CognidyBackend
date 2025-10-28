from google import genai
from config.env_config import get_env_config
from database import get_puzzles_collection
from constants.collections import Collection
import json
from datetime import datetime


env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def generate_user_puzzles(file, user_id):
    try:
        genai_file = genai_client.files.upload(file=file)

        prompt = """
        Based on the content of the uploaded file, generate a crossword puzzle in JSON format for a Next.js frontend.
        
        Requirements:
        1. Extract 8-12 key terms from the file content
        2. Create a 15x15 crossword grid
        3. Use null for empty cells, letters for filled cells, and numbers for word starts
        4. Ensure words intersect logically
        
        Return ONLY valid JSON with this exact structure:
        {
          "metadata": {
            "title": "Generated from [filename]",
            "difficulty": "easy|medium|hard",
            "gridSize": {"rows": 15, "cols": 15},
            "totalWords": [number]
          },
          "grid": [
            // 15x15 array where null = empty cell, letters for filled cells
          ],
          "words": [
            {
              "number": 1,
              "word": "EXAMPLE",
              "direction": "across|down",
              "startRow": 0,
              "startCol": 0,
              "length": 7,
              "hint": "Definition or context clue"
            }
          ],
          "hints": {
            "across": [{"number": 1, "hint": "..."}],
            "down": [{"number": 2, "hint": "..."}]
          }
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

        # Save to database if user_id provided
        if user_id is not None:
            puzzles_collection = get_puzzles_collection()
            
            # Create puzzle document
            puzzle_document = {
                "user_id": user_id,
                "puzzle_id": user_id + "_" + str(int(datetime.now().timestamp() * 1000)),
                "puzzle_data": puzzle_data,
                "created_at": str(datetime.now()),
                "completed": False,
                "completion_time": None
            }
            
            # Insert into database
            result = puzzles_collection.insert_one(puzzle_document)
            puzzle_document["_id"] = str(result.inserted_id)
            
            return puzzle_document
        
        return puzzle_data
        
    except Exception as error:
        print(f"Error generating puzzles: {error}")
        if 'genai_file' in locals() and genai_file.name:
            genai_client.files.delete(name=genai_file.name)
        return None