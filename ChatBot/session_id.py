import re

def extract_sessions_id(session_str: str):

    # Find the session ID
    match = re.search(r"sessions/(.x?)/contexts", session_str)

    if match:
        session_id = match.group(1)
        print("Session ID:", session_id)
        return session_id

    else:
        print("Session ID not found")
        return " "


def get_string(food_dict : dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])