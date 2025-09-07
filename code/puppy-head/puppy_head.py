# ===========================================================================
# Project: FREISA
# Folder:  /code/puppy-head
# File:    puppy_head.py
#
# ===========================================================================
# **NOTE**: In order to test the code on your puppy, some assets must uploaded:
#
# /home/ubuntu/FREISA/assets/faces:
# - TODO
#
# /home/ubuntu/FREISA/assets/sounds:
# - <https://pixabay.com/sound-effects/small-dog-barking-84707/>
#
# ===========================================================================
# Next steps (TODO: Create issues in openai-devpost-hackathon if not done)
#
# - [ ] Retrieve faces_dir from env variable FREISA_FACE_PATH
#
# - [ ] Allow faces_dir to be a list of directories 
# (with a same format of env var PATH)
# so that if on_fresa we can also include "/var/lib/xxx"
#
# - [ ] Do the same for FREISA_SOUND_PATH
#
# - [ ] Canonicize faces_dir to remove extra "../" in faces_dir and sound_dir
#
# - [ ] Take inspiration from
# <https://github.com/mangdangroboticsclub/apps-md-robots/tree/main/facial-expression-app>
#
# - [ ] Check <https://github.com/suno-ai/bark>
# ===========================================================================

from flask import Flask, jsonify, request
from os import listdir
from os.path import dirname, isfile, join

print(f"INFO: {__file__}")

on_freisa = False

# Try importing package "MangDang". Fallback to simulation on error
try:
    from MangDang.mini_pupper.display import Display, BehaviorState

    on_freisa = True
    print("DEBUG: Running on FREISA")
except ImportError:
    print("WARNING: Running in simulation")


app = Flask(__name__)

if on_freisa:
    faces_dir = "/home/ubuntu/FREISA/assets/faces"
else:
    faces_dir = join(dirname(__file__), "../../assets/faces")
print(f"DEBUG: faces_dir={faces_dir}")

# In-memory storage for known faces
# available_faces = ["sad", "happy", "thinking"] (MOCK)

# Retrieve the list of all "*.png" files in faces_dir
all_images = [
    join(faces_dir, f)
    for f in listdir(faces_dir)
    if isfile(join(faces_dir, f)) and f[-4:] == ".png"
]
print(f"DEBUG: len={len(all_images)}, all_images={all_images}")

available_faces = all_images
current_face = None

if on_freisa:
    sounds_dir = "/home/ubuntu/FREISA/assets/sounds"
else:
    sounds_dir = join(dirname(__file__), "../../assets/sounds")
print(f"DEBUG: sounds_dir={sounds_dir}")

# In-memory storage for known sounds
# available_sounds = ["bark", "woof", "whine"] (MOCK)

# Discover available sounds from sounds_dir
all_sounds = [
    join(sounds_dir, f)
    for f in listdir(sounds_dir)
    if isfile(join(sounds_dir, f)) and f[-4:] == ".mp3"
]
print(f"DEBUG: len={len(all_sounds)}, all_sounds={all_sounds}")
available_sounds = all_sounds

# TODO: Should we need a mapping between sentiment and filename?

@app.route("/status", methods=["GET"])
def list_known_faces():
    return jsonify(
        {"faces_dir": faces_dir,
         "sounds_dir": sounds_dir,
         "available_faces": available_faces,
         "available_sounds": available_sounds}
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


@app.route("/play/sound", methods=["POST"])
def play_sound():
    # TODO: Check if input file exists
    # TODO: Check if output device exists
    # See `demos/audio_test.py` in branch `mini_pupper_2pro_bsp`
    # of <https://github.com/mangdangroboticsclub/mini_pupper_2_bsp>
    ...
    return jsonify({"status": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# EOF
