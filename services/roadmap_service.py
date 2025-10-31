import json
import copy
import time
from google import genai
from config.env_config import get_env_config
from constants.roadmap_prompt import get_roadmap_prompt
from controllers.goals_controller import create_user_goal, delete_user_goal_by_id
from database import get_roadmap_goals_collection
from services.notes_service import update_note_status
from utils.gemini_utils import parse_model_output
from utils.notes_utils import remove_tmp_file, save_tmp_file

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def get_previous_goals(user_id):
    previous_goals = get_roadmap_goals_collection().find({"user_id":user_id}, {"brief": 0, "user_id": 0, "note_id": 0})
    previous_goals = previous_goals.to_list()

    return json.dumps(previous_goals, default=str)

def generate_roadmap_goals(file, user_id, file_id):
    previous_goals = get_previous_goals(user_id)
    prompt = get_roadmap_prompt(previous_goals)

    try:
        genai_file = genai_client.files.upload(file=file)
    except Exception as error:
        print(error)
        return False, "[E] failed to upload file to gemini"

    try:
        contents = [genai.types.Content(role="user", parts=[genai.types.Part(text=prompt)])]

        response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
        )
    except Exception as error:
        print(error)
        return False, "[E] Failed to generate goals"

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

    for goal in response_obj:
        goal_copy = copy.deepcopy(goal)
        create_user_goal(user_id, goal_copy, file_id)

        if "_id" in goal:
            success, msg = delete_user_goal_by_id(goal["_id"], user_id)
            print(success, msg)

def generate_roadmap_goals_background(file_bytes, file_ext, user_id, file_id):
    try:
        goals_file = save_tmp_file(file_bytes, file_ext)
        success, msg = generate_roadmap_goals(goals_file, user_id, file_id)
        # success, msg = test()
        print(msg)
        update_note_status(user_id, file_id, "goals", "done" if success else "failed")
    except Exception as e:
        print(f"[E] Goal generation failed: {e}")
        update_note_status(user_id, file_id, "goals", "failed")
    else:
        remove_tmp_file(goals_file)

def test():
    time.sleep(12)
    return True, "completed testing...."
