# ===========================================================================
# Project: FREISA
# Folder:  /code/puppy-state-api
# File:    puppy_state_manager.py
# ===========================================================================
#
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
# **NOTE 4**: Should update puppy_config.json file based on the actual state
# machine, faces and sounds.
#
# Example: on the host:
#
# scp Downloads/small-dog-barking-84707.mp3 \
#     puppygm03:FREISA/assets/sounds
#
# Inspired by:
# <https://github.com/mangdangroboticsclub/apps-md-robots/tree/main/facial-expression-app>
# ===========================================================================


import json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Protocol

import sounddevice as sd
import soundfile as sf


class DisplayProtocol(Protocol):
    """Protocol for display objects"""

    def show_image(self, image_path: str) -> None:
        """Show image on display"""


@dataclass
class StateDefinition:
    """Data class representing a PuppyStateManager state definition"""

    name: str
    face: Optional[str] = None
    sound: Optional[str] = None
    valid_transitions: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.valid_transitions is None:
            self.valid_transitions = []


@dataclass
class StateConfig:
    """Data class representing the entire PuppyStateManager state configuration"""

    states: List[StateDefinition]
    initial_state: str


@dataclass
class PuppyFace:
    """Data class representing a face of the puppy"""

    name: str
    path: str | Path


@dataclass
class PuppySound:
    """Data class representing a sound that can be played by the puppy"""

    name: str
    path: str | Path


class PuppyStateManager:
    """Manage puppy states following specified state machine"""

    def __init__(self, states_file: str | Path) -> None:
        try:
            from MangDang.mini_pupper.display import Display  # , BehaviorState

            self._is_simulation: bool = False
            self._display: Optional[DisplayProtocol] = Display()
            print("MangDang module imported, running on FREISA!")
        except ImportError:
            self._is_simulation = True
            self._display = None
            print(
                "MangDang module NOT imported, running as simulation! Actions from FREISA will be printed on screen"
            )

        self._lock: Lock = Lock()
        self._states: Dict[str, StateDefinition] = {}
        self._curr_state: Optional[StateDefinition] = None
        self._initial_state: Optional[StateDefinition] = None

        self._load_states(states_file)

    def _load_states(self, states_file: str | Path) -> None:
        """Load states from JSON file"""
        with self._lock:
            try:
                with open(states_file, "r", encoding="utf-8") as f:
                    content: Dict[str, Any] = json.load(f)

                    state_defs: List[StateDefinition] = []
                    for state_data in content["states"]:
                        state_def = StateDefinition(
                            name=state_data["name"],
                            face=state_data.get("face"),
                            sound=state_data.get("sound"),
                            valid_transitions=state_data.get("validTransitions", []),
                        )
                        state_defs.append(state_def)

                    self._states = {s.name: s for s in state_defs}

                    initial_state_name: str = content["initialState"]
                    if initial_state_name not in self._states:
                        raise ValueError(
                            f"Initial state '{
                                initial_state_name}' not found in states"
                        )

                    self._initial_state = self._states[initial_state_name]
                    self._curr_state = self._initial_state

                    face_defs: List[PuppyFace] = []
                    for sound_data in content["faces"]:
                        face = PuppyFace(
                            name=sound_data["name"], path=sound_data["path"]
                        )
                        face_defs.append(face)

                    self._faces = {f.name: f for f in face_defs}

                    sound_defs: List[PuppySound] = []
                    for sound_data in content["sounds"]:
                        sound = PuppySound(
                            name=sound_data["name"], path=sound_data["path"]
                        )
                        sound_defs.append(sound)

                    self._sounds = {s.name: s for s in sound_defs}

                    self._apply_state(self._initial_state)
            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
                self._states = {}
                self._initial_state = None
                self._curr_state = None
                print(f"ERROR: Failed to load states file: {e}")

    def get_states_list(self) -> List[str]:
        """Get list of available state names"""
        return list(self._states.keys())

    def get_current_state(self) -> Optional[str]:
        """Get the name of the current state"""
        return self._curr_state.name if self._curr_state else None

    def transition_to(self, next_state_name: str) -> bool:
        """
        Transition to a state

        Args:
            next_state_name: Name of the state to transition to

        Returns:
            True if transition was successful, False otherwise
        """
        if self._curr_state is None:
            print("ERROR: No current state set")
            return False

        if next_state_name not in self._states:
            print(f"ERROR: State '{next_state_name}' does not exist")
            return False

        if (
            self._curr_state.valid_transitions is None
            or next_state_name not in self._curr_state.valid_transitions
        ):
            print(
                f"ERROR: Invalid transition from '{
                    self._curr_state.name}' to '{next_state_name}'"
            )
            return False

        with self._lock:
            next_state = self._states[next_state_name]
            self._apply_state(next_state)
            self._curr_state = next_state
            return True

    def reset(self) -> None:
        """Reset state to initial value"""
        if self._initial_state is None:
            print("ERROR: No initial state defined")
            return

        with self._lock:
            self._apply_state(self._initial_state)
            self._curr_state = self._initial_state

    def _apply_state(self, state: StateDefinition) -> None:
        """Apply the effects of a state (face and sound)"""
        if state.face:
            self.set_face(state.face)
        if state.sound:
            self.play_sound(state.sound)

    def set_face(self, face_name: str) -> bool:
        """Set the display face"""
        if face_name not in self.get_faces():
            print(f"ERROR: Face '{face_name}' does not exist")
            return False
        if self._is_simulation:
            print(f"[SIM] Changing face to {face_name}")
        elif self._display:
            self._display.show_image(face_name)
        return True

    def play_sound(self, sound_name: str) -> bool:
        """Play a sound (placeholder implementation)"""
        if sound_name not in self.get_sounds():
            print(f"ERROR: Sound '{sound_name}' does not exist")
            return False
        if self._is_simulation:
            print(f"[SIM] Playing sound {sound_name}")
        else:
            # See `demos/audio_test.py` in branch `mini_pupper_2pro_bsp`
            # of <https://github.com/mangdangroboticsclub/mini_pupper_2_bsp>
            sound_path = self._sounds[sound_name].path
            if not os.path.exists(sound_path):
                print(f"ERROR: Sound file '{sound_path}' does not exist")
                return False

            data, samplerate = sf.read(sound_path)

            devices = sd.query_devices()
            print(f"DEBUG: Available audio devices: {devices}")
            if len(devices) == 0:
                print("ERROR: No audio devices available")
                return False

            # Set the default output device to the first one available
            sd.default.device = 0

            # Set the default speaker volume to maximum
            os.system("amixer -c 0 sset 'Headphone' 100%")

            # NOTE: at the moment only .wav files seem to work with sounddevice module
            if str(sound_path).endswith(".wav"):
                sd.play(data, samplerate)
                sd.wait()
            # backup: use command-line tools
            elif str(sound_path).endswith(".mp3"):
                os.system(f"mpg123 {sound_path}")
            else:
                os.system(f"aplay {sound_path}")

            print("DEBUG: Audio playback end")

        return True

    def get_faces(self) -> List[str]:
        """Get list of available face names"""
        return list(self._faces.keys())

    def get_sounds(self) -> List[str]:
        """Get list of available sound names"""
        return list(self._sounds.keys())


# EOF
