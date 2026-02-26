import re
import json

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def check_regex(message):
    config = load_config()
    patterns = config.get("regex_blacklist", [])

    for pattern in patterns:
        if re.search(pattern, message):
            return True

    return False
