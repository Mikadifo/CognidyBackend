import re
import json


def parse_model_output(text: str):
    text = re.sub(r"^```(?:json)?\n", "", text)
    text = re.sub(r"\n```$", "", text)
    text = text.strip()

    json_start = min([i for i in (text.find("["), text.find("{")) if i != -1])
    json_text = text[json_start:]

    return json.loads(json_text)
