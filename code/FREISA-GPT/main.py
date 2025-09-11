import asyncio
import os
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv

from mcp_client_pupper.main import main
from mcp_client_pupper.puppy_voice_assistant import PuppyVoiceAssistant

BASE_URL = "https://open-webui.dmhosted.duckdns.org"
DEFAULT_MODEL = "gpt-oss:20b"
ROSBRIDGE_ADDRESS = "ws://localhost:9090"

if __name__ == "__main__":
    load_dotenv()
    parser = ArgumentParser()
    parser.add_argument(
        "--base-url",
        type=str,
        help="Base URL to reach the LLM (without path)",
        default=os.getenv("OPENAI_BASE_URL", BASE_URL),
    )
    parser.add_argument(
        "--model",
        type=str,
        help="LLM model. To be chosen among the ones available at the specified `--base-url`",
        default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
    )
    parser.add_argument(
        "--server-config",
        type=Path,
        help="Path to the MCP server configuration JSON file.",
        default=Path("./mcp_client_pupper/servers_config.json"),
    )
    parser.add_argument(
        "--input-device",
        type=int,
        default=None,
        help="Id of The input device (aka microphone)\n" f"available devices {PuppyVoiceAssistant.available_devices()}",
    )
    parser.add_argument(
        "--whisper-model",
        default="small.en",
        type=str,
        help="Whisper.cpp model, default to %(default)s",
    )
    parser.add_argument(
        "--silence-threshold",
        default=16,
        type=int,
        help="The duration of silence after which the inference will be running, default to %(default)s",
    )
    parser.add_argument(
        "--block-duration",
        default=30,
        help="Minimum time audio updates in ms, default to %(default)s",
    )
    args = parser.parse_args()

    asyncio.run(main(args))
