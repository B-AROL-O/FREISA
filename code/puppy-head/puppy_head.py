from flask import Flask, request, jsonify

# TODO: Take inspiration from
# <https://github.com/mangdangroboticsclub/apps-md-robots/tree/main/facial-expression-app>

# TODO: Attempt to import MangDang. Fallback to simulation on error
# from MangDang.mini_pupper.display import Display, BehaviorState

app = Flask(__name__)

# In-memory storage for known faces
# TODO: discover available faces from "../../../assets/faces"
available_faces = ["alice", "bob", "charlie"]
current_face = None

available_sounds = ["bark", "woof", "sign"]

# TODO: Should we need a mapping between sentiment and filename?


@app.route("/status", methods=["GET"])
def list_known_faces():
    return jsonify(
        {"available_faces": available_faces, "available_sounds": available_sounds}
    )


@app.route("/face/set", methods=["POST"])
def set_face():
    global current_face
    data = request.get_json()
    if not data or "new_face_id" not in data:
        return jsonify({"error": "Missing new_face_id"}), 400

    new_face_id = data["new_face_id"]

    if new_face_id not in available_faces:
        return jsonify({"error": f"Face '{new_face_id}' not recognized"}), 404

    # TODO: Load the picture using MangDang.display
    # disp = Display()
    # disp.show_image('/var/lib/mini_pupper_bsp/test.png')

    current_face = new_face_id
    return jsonify({"message": f"Current face set to {current_face}"}), 200


# @app.route("/play/sound", methods=["POST"])
# def play_sound():
#     See <https://github.com/mangdangroboticsclub/mini_pupper_2_bsp/blob/mini_pupper_2pro_bsp/demos/audio_test.py>
#     ...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# EOF
