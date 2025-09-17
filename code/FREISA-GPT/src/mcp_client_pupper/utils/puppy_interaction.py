import logging
from typing import Dict, Optional, Tuple

import httpx
from icecream import ic

logger = logging.getLogger(__name__)


async def parse_action(puppy_api_url: str, action: str) -> bool:
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
        ok, _ = await call_api(puppy_api_url, "/api/v1/sound", method="POST", data={"sound": sound_name})
        return ok

    if action.startswith("set_face:"):
        face_name = action.split("set_face:")[1]
        ic(f"Setting face: {face_name}")
        ok, _ = await call_api(puppy_api_url, "/api/v1/face", method="POST", data={"face": face_name})
        return ok

    if action.startswith("state:"):
        state_name = action.split("state:")[1]
        ic(f"Setting state: {state_name}")
        ok, _ = await call_api(puppy_api_url, "/api/v1/state", method="POST", data={"state": state_name})
        return ok

    if action.startswith("reset"):
        ic("Resetting puppy state")
        ok, _ = await call_api(puppy_api_url, "/api/v1/reset", method="POST", data={})
        return ok

    ic(f"Unknown action: {action}")
    return False


async def call_api(
    base_url: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None
) -> Tuple[bool, Dict | None]:
    """Wrapper to call the puppy API"""

    url = f"{base_url}{endpoint}"
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=120)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers, timeout=120)
            else:
                raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
    except httpx.RequestError as e:
        logger.error(f"Error calling Puppy API: {str(e)}")

        if isinstance(e, httpx.HTTPStatusError):
            status_code = e.response.status_code
            logger.error(f"Status code: {status_code}")
            logger.error(f"Response details: {e.response.text}")

        return False, None

    if response.status_code in [200, 204]:
        res_content = response.json if response.content else None
        return True, res_content

    logger.error(f"Pupper API call failed: {response.status_code} - {response.text}")
    return False, None
