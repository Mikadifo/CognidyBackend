import os
import json
import uuid
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
import google.generativeai as genai
from config.env_config import get_env_config

env = get_env_config()
genai.configure(api_key=env.GENAI_API_KEY)

UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_crossword_prompt():
    return """
You are a crossword puzzle generator. Generate a crossword puzzle from the uploaded file content.

CRITICAL INSTRUCTIONS:
1. Read the file content and extract 6-10 key terms (3-8 letters each)
2. Create a crossword grid where words INTERSECT by sharing common letters
3. Use a 15x15 grid maximum for web display
4. Return ONLY valid JSON - no markdown, no explanations, no extra text

CROSSWORD RULES:
- Words must intersect at shared letters (e.g., CAT and TAR share 'T')
- Place longer words first, then fit shorter words that intersect
- Number each word starting from 1
- Include clear, educational hints for each word

REQUIRED JSON FORMAT (follow exactly):
{
  "metadata": {
    "puzzleID": "auto_generated_timestamp",
    "title": "Crossword from [filename]",
    "completed": false,
    "gridSize": 15
  },
  "answerGrid": [
    // Array of 15 arrays, each with 15 elements
    // Use UPPERCASE letters for filled cells: "C", "A", "T"
    // Use null for empty cells
    // Example row: ["C", "A", "T", null, null, "D", "O", "G", null, null, null, null, null, null, null]
  ],
  "userGrid": [
    // Array of 15 arrays, each with 15 elements
    // ALL elements must be null (empty for user to fill)
    // Example row: [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null]
  ],
  "words": [
    {
      "number": 1,
      "word": "EXAMPLE",
      "direction": "across",
      "startRow": 0,
      "startCol": 0,
      "length": 7,
      "hint": "Sample or instance"
    }
  ]
}

VALIDATION CHECKLIST:
✓ All grid arrays have exactly 15 rows and 15 columns
✓ answerGrid uses UPPERCASE letters and null only
✓ userGrid uses null only
✓ Each word fits within grid boundaries
✓ Intersecting words share the same letter at intersection points
✓ Word positions (startRow, startCol) are 0-based indices
✓ All hints are educational and clear

EXAMPLE (6x6 for clarity):
{
  "metadata": {"puzzleID": "123", "title": "Sample", "completed": false, "gridSize": 6},
  "answerGrid": [
    ["C", "A", "T", null, null, null],
    [null, null, "A", null, null, null],
    [null, null, "R", "A", "T", null],
    [null, null, null, "R", null, null],
    [null, null, null, "T", null, null],
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
    {"number": 1, "word": "CAT", "direction": "across", "startRow": 0, "startCol": 0, "length": 3, "hint": "Feline pet"},
    {"number": 2, "word": "TAR", "direction": "down", "startRow": 0, "startCol": 2, "length": 3, "hint": "Road material"},
    {"number": 3, "word": "RAT", "direction": "across", "startRow": 2, "startCol": 2, "length": 3, "hint": "Small rodent"},
    {"number": 4, "word": "ART", "direction": "down", "startRow": 2, "startCol": 3, "length": 3, "hint": "Creative work"}
  ]
}

Now generate a crossword puzzle from the provided content.
"""

def validate_file(file):
    """Validate uploaded file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return False, "Only .txt and .pdf files are allowed"
    
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    return True, "Valid file"

def extract_text_content(file_path, content_type):
    """Extract text from uploaded file"""
    try:
        if content_type == 'text/plain':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content.strip()
        elif content_type == 'application/pdf':
            return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def validate_crossword_data(data):
    """Validate the structure of generated crossword data"""
    required_fields = ['metadata', 'answerGrid', 'userGrid', 'words']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    metadata = data['metadata']
    if 'gridSize' not in metadata:
        return False, "Missing gridSize in metadata"
    
    grid_size = metadata['gridSize']
    answer_grid = data['answerGrid']
    user_grid = data['userGrid']
    
    if not isinstance(answer_grid, list) or len(answer_grid) != grid_size:
        return False, f"answerGrid must be {grid_size}x{grid_size} array"
    
    if not isinstance(user_grid, list) or len(user_grid) != grid_size:
        return False, f"userGrid must be {grid_size}x{grid_size} array"
    
    for i, (answer_row, user_row) in enumerate(zip(answer_grid, user_grid)):
        if not isinstance(answer_row, list) or len(answer_row) != grid_size:
            return False, f"answerGrid row {i} must have {grid_size} elements"
        if not isinstance(user_row, list) or len(user_row) != grid_size:
            return False, f"userGrid row {i} must have {grid_size} elements"
    
    if not isinstance(data['words'], list) or len(data['words']) == 0:
        return False, "Must have at least one word"
    
    return True, "Valid crossword data"

def generate_crossword_puzzle(file):
    """Generate crossword puzzle from uploaded file"""
    if file is None:
        return {"success": False, "error": "No file provided"}
    
    is_valid, message = validate_file(file)
    if not is_valid:
        return {"success": False, "error": message}
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(file_path)
        
        text_content = extract_text_content(file_path, file.content_type)
        if not text_content:
            return {"success": False, "error": "Could not extract text from file"}
        
        if len(text_content) < 100:
            return {"success": False, "error": "File content too short. Please provide more substantial notes (at least 100 characters)."}
        
        try:
            prompt = create_crossword_prompt()
            full_prompt = f"{prompt}\n\nFile content:\n{text_content}"
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(full_prompt)
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                puzzle_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"AI returned invalid JSON: {str(e)}"}
            
            is_valid_puzzle, validation_message = validate_crossword_data(puzzle_data)
            if not is_valid_puzzle:
                return {"success": False, "error": f"Invalid puzzle structure: {validation_message}"}
            
            puzzle_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            puzzle_data['metadata']['puzzleID'] = puzzle_id
            puzzle_data['metadata']['title'] = f"Crossword from {filename}"
            
            return {
                "success": True,
                "puzzle": puzzle_data
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error generating crossword: {str(e)}"}
                    
    except Exception as e:
        return {"success": False, "error": f"Error generating crossword: {str(e)}"}
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)