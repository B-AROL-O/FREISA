import logging
import os

from .mcp_client import ChatSessionConfig
from .puppy_voice_assistant import PuppyVoiceAssistant, VoiceConfig
from .utils.llm_client import LLMClientConfig

"""
FREISA-GPT entrypoint
"""


logging.basicConfig(
    level=os.getenv("FREISA_LOG_LEVEL", "DEBUG"),
    format="%(asctime)s [%(levelname)-8s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main(args):
    api_key = os.getenv("OPENAI_API_KEY")

    chat_config = ChatSessionConfig(
        mcp_server_config_file=args.mcp_server_config,
        llm_client_config=LLMClientConfig(base_url=args.llm_base_url, model=args.llm_model, api_key=api_key),
    )
    voice_config = VoiceConfig(
        model=args.whisper_model,
        input_device=args.input_device,
        silence_threshold=args.silence_threshold,
        block_duration=args.block_duration,
    )
    voice_assistant = PuppyVoiceAssistant(voice_config, chat_config, args.puppy_api_url)
    voice_assistant.start()
