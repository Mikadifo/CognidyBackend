from google import genai
from config.env_config import get_env_config

env = get_env_config()
genai_client = genai.Client(api_key=env.GENAI_API_KEY)

def generate_roadmap_goals(file):
    try:
        genai_file = genai_client.files.upload(file=file)

        #TODO: call prompt here

        if genai_file.name is not None:
            genai_client.files.delete(name=genai_file.name)

        # TODO: save to DB

        return [4,5,6] # TODO: return generated array here
    except Exception as error:
        # TODO; handle errors
        return None

