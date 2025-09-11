"""
This module constitutes the Speech To Text (STT) part of the architecture.
Its main purpose is to listen to the microphone, detect speech, and convert
it to text using `pywhispercpp`.
If the text matches a wakeup command, the assistent will listen for the next
command and send it to the LLM, that will generate a response for the puppy.
"""

import importlib.metadata
import logging
import queue
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import numpy as np
import sounddevice as sd
import webrtcvad
from pywhispercpp import constants
from pywhispercpp.model import Model
from utils.math import similarity
from utils.puppy_interaction import parse_action

from mcp_client_pupper.mcp_client import ChatSession

__version__ = importlib.metadata.version("pywhispercpp")

__header__ = f"""
=====================================
FREISA Puppy Voice Assistant

An STT assistant that uses whisper.cpp and a LLM to interact with your puppy.

Using `pywhispercpp` version {__version__}.
Inspired by: https://github.com/absadiki/pywhispercpp/blob/main/pywhispercpp/examples/assistant.py
=====================================
"""


@dataclass
class VoiceConfig:
    model: str = "base.en"
    input_device: Optional[int] = None
    silence_threshold: int = 8
    q_threshold: int = 16
    block_duration: int = 30
    wakeup_command: str = "Hello puppy"
    model_params: Dict[Any, Any] = {}


class PuppyVoiceAssistant:
    """
    PuppyVoiceAssistant class

    Example usage
    ```python
    import os
    from llm import LLM

    llm = LLM(
        model=os.getenv("OPENAI_MODEL", "gpt-oss:20b"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    my_assistant = PuppyVoiceAssistant(
        llm=llm,
        model="tiny.en",
        commands_callback=print,
        n_threads=8
    )
    my_assistant.start()
    ```
    """

    def __init__(
        self,
        voice_config: VoiceConfig,
        chat_session: ChatSession,
        puppy_api_url: str,
        commands_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        :param llm: The LLM instance to use to process the commands
        :param model: whisper.cpp model name or a direct path to a`ggml` model
        :param input_device: The input device (aka microphone), keep it None to take the default
        :param silence_threshold: The duration of silence after which the inference will be running
        :param q_threshold: The inference won't be running until the data queue is having at least `q_threshold`
            elements
        :param block_duration: minimum time audio updates in ms
        :param commands_callback: The callback to run when a command is received
        :param wakeup_command: The command to wake up the assistant
        :param model_params: any other parameter to pass to the whsiper.cpp model see :::
            pywhispercpp.constants.PARAMS_SCHEMA
        """

        self.chat_session = chat_session

        self.puppy_api_url = puppy_api_url
        self.input_device = voice_config.input_device
        self.sample_rate = constants.WHISPER_SAMPLE_RATE  # same as whisper.cpp
        self.channels = 1  # same as whisper.cpp
        self.block_duration = voice_config.block_duration
        self.block_size = int(self.sample_rate * self.block_duration / 1000)
        self.q = queue.Queue()

        self.vad = webrtcvad.Vad()
        self.silence_threshold = voice_config.silence_threshold
        self.q_threshold = voice_config.q_threshold
        self._silence_counter = 0

        self.pwccp_model = Model(
            voice_config.model,
            print_realtime=False,
            print_progress=False,
            print_timestamps=False,
            single_segment=True,
            no_context=True,
            **voice_config.model_params,
        )
        self.commands_callback = commands_callback

        self.wakeup_command = voice_config.wakeup_command
        self.waiting_cmd_prompt = True

    def _audio_callback(self, indata, frames, time, status):
        """
        This is called (from a separate thread) for each audio block.
        """
        if status:
            logging.warning("underlying audio stack warning: %s", status)

        assert frames == self.block_size
        # normalize from [-1,+1] to [0,1]
        audio_data = map(lambda x: (x + 1) / 2, indata)
        audio_data = np.fromiter(audio_data, np.float16)
        audio_data = audio_data.tobytes()
        detection = self.vad.is_speech(audio_data, self.sample_rate)
        if detection:
            self.q.put(indata.copy())
            self._silence_counter = 0
        else:
            if self._silence_counter >= self.silence_threshold:
                if self.q.qsize() > self.q_threshold:
                    heard = self._transcribe_speech()
                    if len(heard) > 0:
                        self._process_heard_text(heard)
                    self._silence_counter = 0
            else:
                self._silence_counter += 1

    def _transcribe_speech(self):
        logging.info("Speech detected ...")
        audio_data = np.array([])
        while self.q.qsize() > 0:
            # get all the data from the q
            audio_data = np.append(audio_data, self.q.get())
        # Appending zeros to the audio data as a workaround for small audio packets (small commands)
        audio_data = np.concatenate([audio_data, np.zeros((int(self.sample_rate) + 10))])
        # running the inference
        segments = self.pwccp_model.transcribe(audio_data, new_segment_callback=self._new_segment_callback)
        # for i, seg in enumerate(segments):
        #     print(f"seg #{i}: {seg.text}")
        return segments[0].text if len(segments) > 0 else ""

    def _new_segment_callback(self, seg):
        if self.commands_callback:
            self.commands_callback(seg.text)

    def _process_heard_text(self, heard):
        if self.waiting_cmd_prompt and similarity(heard, self.wakeup_command) > 0.8:
            print(f"heard activation command '{self.wakeup_command}'")
            # reset state machine to be sure that listening is possible
            parse_action(self.puppy_api_url, "reset")
            self.waiting_cmd_prompt = False
            parse_action(self.puppy_api_url, "state:listening")
        elif not self.waiting_cmd_prompt:
            print(f"heard command '{heard}'")
            parse_action(self.puppy_api_url, "state:thinking")
            _ = self.chat_session.process_user_request_sync(heard)
            parse_action(self.puppy_api_url, "state:proud")
            # TODO: see how to fix it
            time.sleep(2)  # wait before accepting again the wakeup command
            parse_action(self.puppy_api_url, "reset")
            self.waiting_cmd_prompt = True

    def start(self) -> None:
        """
        Use this function to start the assistant
        :return: None
        """
        logging.info("Starting Assistant ...")
        with sd.InputStream(
            device=self.input_device,  # the default input device
            channels=self.channels,
            samplerate=constants.WHISPER_SAMPLE_RATE,
            blocksize=self.block_size,
            callback=self._audio_callback,
        ):
            try:
                logging.info("Assistant is listening ... (CTRL+C to stop)")
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                logging.info("Assistant stopped")

    @staticmethod
    def available_devices():
        """
        List all the available audio capture devices

        :return: a list of available devices
        """
        return sd.query_devices()
