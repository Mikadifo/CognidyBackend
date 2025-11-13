import json
import time
from bson import ObjectId
from google import genai
from config.env_config import get_env_config
from constants.quizzes_prompt import get_quizzes_prompt
from database import get_quizzes_collection
from services.notes_service import update_note_status
from utils.gemini_utils import parse_model_output
from utils.notes_utils import remove_tmp_file, save_tmp_file

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def get_previous_quizzes(user_id):
    previous_quizzes = get_quizzes_collection().find({"user_id":user_id}, {"brief": 0, "user_id": 0, "note_id": 0})
    previous_quizzes = previous_quizzes.to_list()

    return json.dumps(previous_quizzes, default=str)

def generate_quizzes(file, user_id, file_id):
    previous_quizzes = get_previous_quizzes(user_id)
    print("Previous quizzes: ", previous_quizzes)
    prompt = get_quizzes_prompt(previous_quizzes)

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
        return False, "[E] Failed to generate quizzes"

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

    for quizz in response_obj:
        if "_id" in quizz:
            get_quizzes_collection().update_one(
                    {"user_id": user_id, "_id": ObjectId(quizz["_id"])},
                    {"$set": {
                        "question": quizz["question"],
                        "options": quizz["options"],
                        "correct": quizz["correct"],
                        "note_id": file_id
                    }}
            )
        else:
            quizz["_id"] = ObjectId()
            quizz["user_id"] = user_id

            if file_id is not None:
                quizz["note_id"] = file_id

            get_quizzes_collection().insert_one(quizz)

def generate_quizzes_background(file_bytes, file_ext, user_id, file_id):
    try:
        quizzes_file = save_tmp_file(file_bytes, file_ext)
        #success, msg = generate_quizzes(quizzes_file, user_id, file_id)
        success, msg = test()
        print(msg)
        update_note_status(user_id, file_id, "quizzes", "done" if success else "failed")
    except Exception as e:
        print(f"[E] Goal generation failed: {e}")
        update_note_status(user_id, file_id, "goals", "failed")
    else:
        remove_tmp_file(quizzes_file)

def test():
    time.sleep(12)
    return True, "completed testing...."
