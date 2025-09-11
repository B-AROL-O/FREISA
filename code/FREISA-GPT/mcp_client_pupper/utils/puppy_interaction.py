import requests
from icecream import ic


def parse_action(puppy_api_url: str, action: str) -> bool:
    """
    Parse the action string.
    If the action is not valid, return False.
    If the action is valid, send the action
    to the robot and return True.

    Valid actions:
    - "play_sound:<sound_name>"
    - "set_face:<face_name>"
    - "state:<state_name>"
    - "reset"
    """

    if action.startswith("play_sound:"):
        sound_name = action.split("play_sound:")[1]
        ic(f"Playing sound: {sound_name}")
        ok, _ = call_api(puppy_api_url, "/api/v1/sound", method="POST", data={"sound": sound_name})
        return ok

    if action.startswith("set_face:"):
        face_name = action.split("set_face:")[1]
        ic(f"Setting face: {face_name}")
        ok, _ = call_api(puppy_api_url, "/api/v1/face", method="POST", data={"face": face_name})
        return ok

    if action.startswith("state:"):
        state_name = action.split("state:")[1]
        ic(f"Setting state: {state_name}")
        ok, _ = call_api(puppy_api_url, "/api/v1/state", method="POST", data={"state": state_name})
        return ok

    if action.startswith("reset"):
        ic("Resetting puppy state")
        ok, _ = call_api(puppy_api_url, "/api/v1/reset", method="POST", data={})
        return ok

    ic(f"Unknown action: {action}")
    return False


def call_api(base_url: str, endpoint: str, method: str = "GET", data: dict = None) -> tuple[bool, dict | None]:
    """Wrapper to call the puppy API"""

    url = f"{base_url}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if method == "GET":
        response = requests.get(url, headers=headers, timeout=120)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers, timeout=120)
    else:
        raise ValueError(f"Unsupported method: {method}")

    if response.status_code in [200, 204]:
        res_content = response.json if response.content else None
        return True, res_content

    ic(f"API call failed: {response.status_code} - {response.text}")
    return False, None
