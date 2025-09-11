import asyncio
import json
import logging
import os
import shutil
from argparse import ArgumentParser
from contextlib import AsyncExitStack
from typing import Any, Callable, Optional

import httpx
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp_client import ChatSession, Server
from puppy_voice_assistant import PuppyVoiceAssistant, VoiceConfig
from utils.llm_client import LLMClient


async def main(args):
    api_key = os.getenv("OPENAI_API_KEY")
    server_config = json.loads(args.mcp_server_config)
    servers = [Server(name, srv_config) for name, srv_config in server_config["mcpServers"].items()]

    llm_client = LLMClient(args.llm_model, args.llm_base_url, api_key)

    # HERE
    chat_session = ChatSession(servers, llm_client)
    voice_config = VoiceConfig(
        model=args.whisper_model,
        input_device=args.input_device,
        silence_threshold=args.silence_threshold,
        block_duration=args.block_duration,
    )
    voice_assistant = PuppyVoiceAssistant(chat_session, args.puppy_api_url)
    await voice_assistant.start()


if __name__ == "__main__":
    pass
