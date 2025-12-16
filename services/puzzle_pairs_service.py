import json
import time
from bson import ObjectId
from google import genai
from config.env_config import get_env_config
from constants.puzzles_pair_prompt import get_puzzles_prompt
from database import get_puzzles_collection
from services.notes_service import update_note_status
from utils.gemini_utils import parse_model_output
from utils.notes_utils import remove_tmp_file, save_tmp_file

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def get_previous_puzzles(user_id):
    previous_puzzles = get_puzzles_collection().find({"user_id":user_id}, {"user_id": 0, "note_id": 0})
    previous_puzzles = previous_puzzles.to_list()

    return json.dumps(previous_puzzles, default=str)

def generate_puzzles(file, user_id, file_id):
    previous_puzzles = get_previous_puzzles(user_id)
    print("Previous puzzles: ", previous_puzzles)
    prompt = get_puzzles_prompt(previous_puzzles)

    try:
        genai_file = genai_client.files.upload(file=file)
    except Exception as error:
        print(error)
        return False, "[E] failed to upload file to gemini"

    try:
        contents = [
                genai.types.Content(
                    role="user",
                    parts=[
                        genai.types.Part(text=prompt),
                        genai.types.Part(file_data=genai.types.FileData(file_uri=genai_file.uri))
                    ]
                )
        ]

        response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
        )
    except Exception as error:
        print(error)
        return False, "[E] Failed to generate puzzles"

    try:
        if genai_file.name is not None:
            genai_client.files.delete(name=genai_file.name)
    except Exception as error:
        print(f"[W] failed to delete file {error}")

    try:
        save_to_DB(response, file_id, user_id)
    except Exception as error:
        print(error)
        return False, "[E] Failed to save to Database"

    return True, ""

def save_to_DB(response, file_id, user_id):
    try:
        print("genai raw response ->", response.text)
        response_obj = parse_model_output(response.text)
        print("genai obj response ->", response_obj)
    except json.JSONDecodeError:
        raise ValueError("Could not parse JSON from model output")

    for puzzle in response_obj:
        if "_id" in puzzle:
            get_puzzles_collection().update_one(
                    {"user_id": user_id, "_id": ObjectId(puzzle["_id"])},
                    {"$set": {
                        "pairs": puzzle["pairs"],
                        "note_id": file_id
                    }}
            )
        else:
            puzzle["_id"] = ObjectId()
            puzzle["user_id"] = user_id

            if file_id is not None:
                puzzle["note_id"] = file_id

            get_puzzles_collection().insert_one(puzzle)

def generate_puzzles_background(file_bytes, file_ext, user_id, file_id):
    try:
        puzzles_file = save_tmp_file(file_bytes, file_ext)
        success, msg = generate_puzzles(puzzles_file, user_id, file_id)
        #success, msg = test()
        print(msg)
        update_note_status(user_id, file_id, "puzzles", "done" if success else "failed")
    except Exception as e:
        print(f"[E] Puzzle generation failed: {e}")
        update_note_status(user_id, file_id, "puzzles", "failed")
    else:
        remove_tmp_file(puzzles_file)

def test():
    time.sleep(12)
    return True, "completed testing...."
