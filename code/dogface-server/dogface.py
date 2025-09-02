from flask import Flask, request, jsonify

# TODO: Take inspiration from
# <https://github.com/mangdangroboticsclub/apps-md-robots/tree/main/facial-expression-app>

# TODO: Attempt to import MangDang. Fallback to simulation on error

app = Flask(__name__)

# In-memory storage for known faces
# TODO: discover available faces from "../../../assets/faces"
available_faces = ["alice", "bob", "charlie"]
current_face = None

# TODO: Should we need a mapping between sentiment and filename?

@app.route("/face/available", methods=["GET"])
def list_known_faces():
    return jsonify({"available_faces": available_faces})

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
    
    current_face = new_face_id
    return jsonify({"message": f"Current face set to {current_face}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# EOF
