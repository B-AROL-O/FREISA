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

# Adapted from
# https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/clients/simple-chatbot/mcp_simple_chatbot/main.py
#
# ---
#
# MIT License
#
# Copyright (c) 2024 Anthropic, PBC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


logger = logging.getLogger(__name__)

BASE_URL = "https://open-webui.dmhosted.duckdns.org"
DEFAULT_MODEL = "gpt-oss:20b"
ROSBRIDGE_ADDRESS = "ws://localhost:9090"


class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_key_env_name: str = "LLM_API_KEY",
    ) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self.api_key_env_name = api_key_env_name
        self.api_key = api_key or os.getenv(api_key_env_name)

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @staticmethod  # TODO: make it classmethod
    def load_config(file_path: str) -> dict[str, Any]:
        """Load server configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            Dict containing server configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:
        """Get the LLM API key.

        Returns:
            The API key as a string.

        Raises:
            ValueError: If the API key is not found in environment variables.
        """
        if not self.api_key:
            raise ValueError(f"{self.api_key_env_name} not found in environment variables")
        return self.api_key


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.stdio_context: Any | None = None
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection."""
        command = shutil.which("npx") if self.config["command"] == "npx" else self.config["command"]
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]} if self.config.get("env") else {**os.environ},
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.session = session
        except Exception as e:
            logger.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> list[Any]:
        """List available tools from the server.

        Returns:
            A list of available tools.

        Raises:
            RuntimeError: If the server is not initialized.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.session.list_tools()
        tools = []

        for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                tools.extend(Tool(tool.name, tool.description, tool.inputSchema, tool.title) for tool in item[1])

        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> Any:
        """Execute a tool with retry mechanism.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            retries: Number of retry attempts.
            delay: Delay between retries in seconds.

        Returns:
            Tool execution result.

        Raises:
            RuntimeError: If server is not initialized.
            Exception: If tool execution fails after all retries.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)

                return result

            except Exception as e:
                attempt += 1
                logger.warning(f"Error executing tool: {e}. Attempt {attempt} of {retries}.")
                if attempt < retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logger.error(f"Error during cleanup of server {self.name}: {e}")


class Tool:
    """Represents a tool with its properties and formatting."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        title: str | None = None,
    ) -> None:
        self.name: str = name
        self.title: str | None = title
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM.

        Returns:
            A formatted string describing the tool.
        """
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = f"- {param_name}: {param_info.get('description', 'No description')}"
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        # Build the formatted output with title as a separate field
        output = f"Tool: {self.name}\n"

        # Add human-readable title if available
        if self.title:
            output += f"User-readable title: {self.title}\n"

        output += f"""Description: {self.description}
Arguments:
{chr(10).join(args_desc)}
"""

        return output


class LLMClient:
    """Manages communication with the LLM provider (OpenWebUI)."""

    chat_endpoint: str = "/api/chat/completions"
    models_endpoint: str = "/api/models"

    def __init__(self, model: str, base_url: str, api_key: str) -> None:
        self.model: str = model
        self.base_url: str = base_url.rstrip("/")
        self.api_key: str = api_key

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM.

        Args:
            messages: A list of message dictionaries ().

        Returns:
            The LLM's response as a string.

        Raises:
            httpx.RequestError: If the request to the LLM fails.
        """
        url = f"{self.base_url}{self.chat_endpoint}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "messages": messages,
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1,
            "stream": False,
            "stop": None,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logger.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logger.error(f"Status code: {status_code}")
                logger.error(f"Response details: {e.response.text}")

            return f"I encountered an error: {error_message}. Please try again or rephrase your request."


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: list[Server], llm_client: LLMClient, puppy_face: PuppyFace) -> None:
        self.servers: list[Server] = servers
        self.llm_client: LLMClient = llm_client
        self.puppy_face = puppy_face

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        for server in reversed(self.servers):
            try:
                await server.cleanup()
            except Exception as e:
                logger.warning(f"Warning during final cleanup: {e}")

    async def process_llm_response(self, llm_response: str) -> str:
        """Process the LLM response and execute tools if needed.

        Args:
            llm_response: The response from the LLM.

        Returns:
            The result of tool execution or the original response.
            If no tool is used, the output contains the original response.
        """
        import json

        try:
            tool_call = json.loads(llm_response)
            if "tool" in tool_call and "arguments" in tool_call:
                logger.info(f"Executing tool: {tool_call['tool']}")
                logger.info(f"With arguments: {tool_call['arguments']}")

                for server in self.servers:
                    tools = await server.list_tools()
                    if any(tool.name == tool_call["tool"] for tool in tools):
                        try:
                            result = await server.execute_tool(tool_call["tool"], tool_call["arguments"])

                            if isinstance(result, dict) and "progress" in result:
                                progress = result["progress"]
                                total = result["total"]
                                percentage = (progress / total) * 100
                                logger.info(f"Progress: {progress}/{total} ({percentage:.1f}%)")

                            return f"Tool execution result: {result}"
                        except Exception as e:
                            error_msg = f"Error executing tool: {str(e)}"
                            logger.error(error_msg)
                            return error_msg

                return f"No server found with tool: {tool_call['tool']}"
            return llm_response
        except json.JSONDecodeError:
            return llm_response

    async def start(self) -> None:
        """Main chat session handler."""
        try:
            for server in self.servers:
                try:
                    await server.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize server: {e}")
                    await self.cleanup_servers()
                    return

            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            tools_description = "\n".join([tool.format_for_llm() for tool in all_tools])

            system_message = (
                "You are an assistant that is used to translate natural language commands coming from the user"
                "into calls to specific Tools that are used to control a quadruped robot running ROS2.\n"
                "Pay attention to what the user says, as his commands come from voice recordings that are translated"
                "to text.\n\n"
                "You have access to these tools:\n\n"
                f"{tools_description}\n"
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: When you need to use a tool, you must ONLY respond with "
                "the exact JSON object format below, nothing else:\n"
                "{\n"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '        "argument-name": "value"\n'
                "    }\n"
                "}\n\n"
                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response\n"
                "2. Keep responses concise but informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Avoid simply repeating the raw data\n\n"
                "Please use ONLY the tools that are explicitly defined above.\n"
                "The first thing you have to do is to use the 'connect_to_robot' tool to connect to the robot"
                f"at the address '{ROSBRIDGE_ADDRESS}'. This only needs to be done once."
            )

            messages = [{"role": "system", "content": system_message}]

            while True:
                try:
                    # TODO: use Whisper
                    user_input = input("You: ").strip().lower()
                    if user_input in ["/quit", "/exit", "/bye"]:
                        logger.info("\nExiting...")
                        break

                    messages.append({"role": "user", "content": user_input})

                    llm_response, _ = asyncio.gather(
                        self.llm_client.get_response(messages),
                        self.puppy_face.set_thinking(),
                    )

                    logger.info("\nAssistant: %s", llm_response)

                    result = await self.process_llm_response(llm_response)

                    if result != llm_response:
                        messages.append({"role": "assistant", "content": llm_response})
                        messages.append({"role": "system", "content": result})

                        final_response = await self.llm_client.get_response(messages)
                        logger.info("\nFinal response: %s", final_response)
                        messages.append({"role": "assistant", "content": final_response})
                    else:
                        messages.append({"role": "assistant", "content": llm_response})

                    await self.puppy_face.set_acting()

                except KeyboardInterrupt:
                    logger.info("\nExiting...")
                    break

        finally:
            await self.cleanup_servers()


# TODO: define methods to query HTTP API -- look at ../puppy-head/ for API
class PuppyFace:
    def __init__(self):
        pass

    async def set_thinking(self):
        pass

    async def set_acting(self):
        pass


async def main(args):
    config = Configuration(api_key=args.api_key)
    server_config = config.load_config("servers_config.json")
    servers = [Server(name, srv_config) for name, srv_config in server_config["mcpServers"].items()]
    llm_client = LLMClient(model=args.model, base_url=args.base_url, api_key=config.llm_api_key)
    puppy_face = PuppyFace()
    chat_session = ChatSession(servers, llm_client, puppy_face)
    await chat_session.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api-key", type=str, help="API key for accessing the LLM", required=False)
    parser.add_argument(
        "--base-url",
        type=str,
        help="Base URL to reach the LLM (without path)",
        default=BASE_URL,
    )
    parser.add_argument("--model", type=str, help="LLM model name to use", default=DEFAULT_MODEL)
    args = parser.parse_args()
    asyncio.run(main(args))
