from google import genai
from config.env_config import get_env_config

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def generate_user_puzzles(file):
    try:
        genai_file = genai_client.files.upload(file=file)

        prompt = """
        Based on the content of the uploaded file, generate a crossword puzzle in JSON format for a Next.js frontend.
        
        Requirements:
        1. Extract 8-12 key terms from the file content
        2. Create a 15x15 crossword grid
        3. Use null for empty cells, letters for filled cells, and numbers for word starts
        4. Ensure words intersect logically
        
        Return JSON with this exact structure:
        {
          "metadata": {
            "title": "Generated from [filename]",
            "difficulty": "easy|medium|hard",
            "gridSize": {"rows": 15, "cols": 15},
            "totalWords": [number]
          },
          "grid": [
            // 15x15 array where:
            // null = empty cell
            // "1", "2", etc = numbered start cells with letters
            // "A", "B", etc = letter cells
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
        
        Important:
        - Words must come from the uploaded file content
        - Hints should be definitions or contextual clues from the file
        - If definitions aren't explicit, infer from context
        - Ensure proper word intersections
        - Number cells should contain both the number AND the first letter
        "Here is an example of the expected JSON format for clarity: [provide a small example here]"
        "{
  "metadata": {
    "title": "Sample Crossword",
    "difficulty": "medium",
    "gridSize": {
      "rows": 15,
      "cols": 15
    },
    "totalWords": 12
  },
  "grid": [
    [null, null, null, "1", "H", "E", "L", "L", "O", null, null, null, null, null, null],
    [null, null, null, null, "U", null, null, null, null, null, null, null, null, null, null],
    [null, "2", "W", "O", "R", "L", "D", null, null, null, null, null, null, null, null],
    [null, null, null, null, "E", null, null, null, null, null, null, null, null, null, null],
    [null, null, null, null, "3", "P", "Y", "T", "H", "O", "N", null, null, null, null]
  ],
  "words": [
    {
      "number": 1,
      "word": "HELLO",
      "direction": "across",
      "startRow": 0,
      "startCol": 3,
      "length": 5,
      "hint": "A greeting"
    },
    {
      "number": 2,
      "word": "WORLD",
      "direction": "across", 
      "startRow": 2,
      "startCol": 1,
      "length": 5,
      "hint": "Planet Earth"
    },
    {
      "number": 1,
      "word": "HUE",
      "direction": "down",
      "startRow": 0,
      "startCol": 3,
      "length": 3,
      "hint": "Color shade"
    },
    {
      "number": 3,
      "word": "PYTHON",
      "direction": "across",
      "startRow": 4,
      "startCol": 4,
      "length": 6,
      "hint": "Programming language"
    }
  ],
  "hints": {
    "across": [
      {
        "number": 1,
        "hint": "A greeting"
      },
      {
        "number": 2, 
        "hint": "Planet Earth"
      },
      {
        "number": 3,
        "hint": "Programming language"
      }
    ],
    "down": [
      {
        "number": 1,
        "hint": "Color shade"
      }
    ]
  }
}" """

        
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, genai_file]
        )

        if genai_file.name is not None:
            genai_client.files.delete(name=genai_file.name)

        # TODO: save to DB


        return [] # TODO: return generated array here
    except Exception as error:
        # TODO; handle errors
        return None
