# ===========================================================================
# Project: FREISA
# Folder:  /code/puppy-state-api
# File:    main.py
# ===========================================================================

import argparse

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from puppy_state_manager import PuppyStateManager

load_dotenv()

app = Flask(__name__)
state_manager = PuppyStateManager("./puppy_config.json")


@app.route("/api/v1/states", methods=["GET"])
def get_available_states():
    """Get available states"""
    return state_manager.get_states_list()


@app.route("/api/v1/state", methods=["POST"])
def set_state():
    """Transition to a new state"""
    data = request.get_json()
    if not data or "state" not in data:
        return jsonify({"error": "Missing state parameter"}), 400

    ok = state_manager.transition_to(data["state"])
    if not ok:
        return jsonify({"error": "Invalid state or transition."}), 400
    return "", 204


@app.route("/api/v1/reset", methods=["POST"])
def reset_to_idle():
    """Reset robot to initial state"""
    state_manager.reset()
    return "", 204


@app.route("/api/v1/faces", methods=["GET"])
def get_available_faces():
    """Get available faces"""
    return state_manager.get_faces()


@app.route("/api/v1/sounds", methods=["GET"])
def get_available_sounds():
    """Get available sounds"""
    return state_manager.get_sounds()


@app.route("/api/v1/face", methods=["POST"])
def set_face():
    """Show a specific face on the display"""
    data = request.get_json()
    if not data or "face" not in data:
        return jsonify({"error": "Missing face parameter"}), 400

    ok = state_manager.set_face(data["face"])
    if not ok:
        return jsonify({"error": "Invalid face."}), 400
    return "", 204


@app.route("/api/v1/sound", methods=["POST"])
def set_sound():
    """Play a specific sound"""
    data = request.get_json()
    if not data or "sound" not in data:
        return jsonify({"error": "Missing sound parameter"}), 400

    ok = state_manager.play_sound(data["sound"])
    if not ok:
        return jsonify({"error": "Invalid sound."}), 400
    return "", 204


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the puppy-state API server.")
    parser.add_argument(
        "--address", default="0.0.0.0", help="IP address to bind the server to"
    )
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    args = parser.parse_args()

    app.run(host=args.address, port=args.port, debug=True)

# EOF
