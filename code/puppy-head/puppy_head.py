# ===========================================================================
# Project: FREISA
# Folder:  /code/puppy-head
# File:    puppy_head.py
#
# ===========================================================================
# **NOTE 1**: See README.md for how to test the code on your puppy.
#
# **NOTE 2**: You must populate assets folders.
#
# **NOTE 3**: Should be tested on a FREISA dog after installing
# some additional assets:
#
# /home/ubuntu/FREISA/assets/faces:
# - TODO
#
# /home/ubuntu/FREISA/assets/sounds:
# - <https://github.com/B-AROL-O/mini_pupper_2_bsp/blob/main/Audio/power_on.mp3>
# - <https://pixabay.com/sound-effects/dog-bark-382732/>
# - <https://pixabay.com/sound-effects/small-dog-barking-84707/>
# - Audio files from Dropbox: 2025-09-03-audio-command-samples
#   (to be converted into 8000 .wav files)
#
# Example: on the host:
#
# scp Downloads/small-dog-barking-84707.mp3 \
#     puppygm03:FREISA/assets/sounds
#
# # ===========================================================================
# Next steps (TODO Create issues in openai-devpost-hackathon if not done)
#
# - [ ] Retrieve faces_dir from env variable FREISA_FACE_PATH
#
# - [ ] Allow faces_dir to be a list of directories
# (using a similar format to environment varriable PATH)
# so that if on_fresa we can also include (for instance)
#
#   - "/var/lib/mini_pupper_bsp"             (install directory)
#   - "/home/ubuntu/mini_pupper_bsp/Display" (working copy)
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
import os
from os import listdir
from os.path import dirname, isfile, join

print(f"INFO: {__file__}")

# Assume we are running on FREISA
# We will fallback to simulation if we discover we are not
on_freisa = True

try:
    # FREISA has MangDang.mini_pupper.display installed
    from MangDang.mini_pupper.display import BehaviorState, Display

except ImportError:
    print("WARNING: Cannot find package MangDang.mini_pupper")
    on_freisa = False

# Try importing python-sounddevice
# https://python-sounddevice.readthedocs.io/
try:
    import sounddevice as sd

except ImportError:
    print("WARNING: Cannot find package sounddevice")
    on_freisa = False
except OSError:
    print("WARNING: Cannot find low-level audio drivers")
    on_freisa = False

# Try importing python-soundfile
# https://python-soundfile.readthedocs.io/
try:
    import soundfile as sf

except ImportError:
    print("WARNING: Cannot find pacakge soundfile")
    on_freisa = False

if on_freisa:
    print("INFO: Running on FREISA approved hardware")
else:
    print("INFO: Running in simulated mode (still useful for development)")

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

available_faces = sorted(all_images)
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
    if isfile(join(sounds_dir, f))
    # and f[-4:] == ".mp3"
    and (
        f.endswith(".mp3")
        or f.endswith(".ogg")
        or f.endswith(".wav")
    )
]
print(f"DEBUG: len={len(all_sounds)}, all_sounds={all_sounds}")
available_sounds = sorted(all_sounds)

# TODO: Should we need a mapping between sentiment and filename?

@app.route("/status", methods=["GET"])
def list_known_faces():
    return jsonify(
        {"faces_dir": faces_dir,
         "sounds_dir": sounds_dir,
         "available_faces": available_faces,
         "available_sounds": available_sounds}
    )


@app.route("/display/set", methods=["POST"])
def set_face():
    global current_face
    data = request.get_json()
    if not data or "path" not in data:
        return jsonify({"error": "Missing path"}), 400

    new_face_path = data["path"]

    if new_face_path not in available_faces:
        return jsonify({"error": f"Path '{new_face_path}' not found"}), 404

    if on_freisa:
        # Load the picture using MangDang.display
        disp = Display()
        # disp.show_image('/var/lib/mini_pupper_bsp/test.png')
        disp.show_image(new_face_path)
    else:
        print(f"DEBUG: Should load {new_face_path}")

    current_face = new_face_path
    return jsonify({
        "status": True,
        "message": f"FREISA face set to {current_face}"}
    ), 200


@app.route("/sound/play", methods=["POST"])
def play_sound():
    data = request.get_json()
    if not data or "path" not in data:
        return jsonify({"error": "Missing path"}), 400
    
    sound_path = data["path"]

    # Check if input path is allowed
    if sound_path not in available_sounds:
        return jsonify({"error": f"Path '{sound_path}' not found"}), 404
    
    # TODO: Check if output device exists
    # See `demos/audio_test.py` in branch `mini_pupper_2pro_bsp`
    # of <https://github.com/mangdangroboticsclub/mini_pupper_2_bsp>

    _ = """
# AUDIO OUTPUT DEVICES ON FREISA HARDWARE (WITHOUT USB ACCESSORIES)

ubuntu@puppygm03:~/FREISA/code/puppy-head$ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7
card 1: sndrpisimplecar [snd_rpi_simple_card], device 0: simple-card_codec_link snd-soc-dummy-dai-0 [simple-card_codec_link snd-soc-dummy-dai-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
ubuntu@puppygm03:~/FREISA/code/puppy-head$
"""

    if on_freisa:
        data, samplerate = sf.read(sound_path)
        print(f"DEBUG: samplerate={samplerate}")
        print(f"DEBUG: Audio playback start: {sound_path}")

        # Audio record parameters
        # fs = 48000  # 48KHz,Audio sampling rate
        # duration = 5  # Recording duration in seconds

        # Set the default speaker volume to maximum
        # Headphone number is 0 without HDMI output
        # Headphone number is 1 when HDMI connect the display
        os.system("amixer -c 0 sset 'Headphone' 100%")

        # TODO Only .wav files seem to work at the moment
        # sd.play(data, fs)
        # sd.wait()  # Wait for playback to finish

        # Backup plan: Use command-line tool "aplay"
        os.system(f"aplay {sound_path}")

        print("DEBUG: Audio playback end")

    return jsonify({
        "status": True,
        "message": f"FREISA is playing {sound_path}"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# EOF
