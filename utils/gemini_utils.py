import re
import json


def parse_model_output(text):
    text = re.sub(r"^```(?:json)?\n", "", text)
    text = re.sub(r"\n```$", "", text)
    text = text.strip()

    return json.loads(text)
