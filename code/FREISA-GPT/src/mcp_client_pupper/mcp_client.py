import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .utils.llm_client import LLMClient, LLMClientConfig
from .utils.puppy_interaction import parse_action

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


@dataclass
class ChatSessionConfig:
    mcp_server_config_file: Path
    llm_client_config: LLMClientConfig


class ChatSession:
    """ChatSession coordinates interactions between the user, the LLM, and the robot's tool interfaces.

    The session lifecycle is:

    1. **Initialization** – receives a list of servers, an LLM client, and a PuppyFace visualizer.
    2. **Server startup** – each server is initialized and its available tools are gathered.
    3. **Main loop** – user input is collected, sent to the LLM, and the LLM's JSON tool call is parsed.
    4. **Tool execution** – matching server executes the requested tool, progress is logged.
    5. **Response handling** – the tool's result is formatted back into a natural‑language reply and sent to the LLM for
       a final response.
    6. **Cleanup** – upon exit or error, all servers are gracefully shut down.

    This docstring explains the overall flow and responsibilities of each component.
    """

    # If system_message is none, can't start.
    system_message: Optional[str] = None
    servers: List[Server] = []
    llm_client: Optional[LLMClient] = None

    def __init__(self, config: ChatSessionConfig) -> None:
        with open(config.mcp_server_config_file) as f:
            self.server_config = json.load(f)

        self.llm_client_config = config.llm_client_config
        self._init_servers()
        self._init_llm_client()

    def _init_servers(self) -> bool:
        self.servers = [Server(name, srv_config) for name, srv_config in self.server_config["mcpServers"].items()]
        return True

    def _init_llm_client(self):
        self.llm_client = LLMClient(self.llm_client_config)
        return self.llm_client.test_connection()

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
        try:
            json_response = json.loads(llm_response)
            if "tool_calls" in json_response and len(json_response["tool_calls"]) > 0:
                for called_tool in json_response["tool_calls"]:
                    tool_name = called_tool["function"]["name"]
                    tool_args = called_tool["function"]["arguments"]
                    logger.info(f"Executing tool: {tool_name}")
                    logger.info(f"With arguments: {tool_args}")

                    # Look for server with right tool:
                    for server in self.servers:
                        tools = await server.list_tools()
                        if any(tool.name == tool_name for tool in tools):
                            try:
                                result = await server.execute_tool(tool_name, tool_args)

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

                    return f"No server found with tool: {tool_name}"
            logger.info("LLM response did not use any tools")
            return llm_response
        except json.JSONDecodeError:
            return llm_response

    async def set_up_mcp_client(self):
        """
        Initialization step.
        It is used to fetch all the tools information and add it to the system prompt (`self.system_message`).
        """
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

            self.system_message = (
                "You are an assistant that is used to translate natural language commands coming from the user"
                "into calls to specific Tools that are used to control a dog-like robot running ROS2.\n"
                "Pay attention to what the user says, as his commands come from voice recordings that are translated"
                "to text.\n"
                "The user is controlling you as if it was talking to a dog, so expect messages of the type: "
                "'Walk forward', or 'Come here'.\n"
                "The user will not give you very detailed description, so you have to assume how a dog would respond "
                "to the voice commands.\n"
                "You have access to these tools:\n\n"
                f"{tools_description}\n"
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: you MUST use a tool every time the user sends a command. "
                "To use a tool, you must ONLY respond with "
                "a list of JSON objects using the SAME EXACT format as below, nothing else:\n"
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
            )

        except Exception as e:
            # Handle exception
            logger.error(e)

    async def process_user_request(self, user_input, url: Optional[str] = None) -> str:
        """Handle a single user request.

        The method follows the same interaction pattern as :pymeth:`start` but is
        intended to be called from the higher‑level voice assistant. It builds a
        short conversation history, sends the user prompt to the LLM, processes
        any tool calls, and returns the final assistant reply.

        Returns:
            str: The assistant's final response.
        """
        if not self.system_message:
            logger.error("System message not set. Call set_up_mcp_client first.")
            return ""

        # Initialise the message list with the system prompt.
        messages = [{"role": "system", "content": self.system_message}]

        logger.debug(f"USER MESSAGE TO LLM: {user_input}")

        if not user_input:
            return ""

        messages.append({"role": "user", "content": user_input})

        try:
            # Send the current conversation to the LLM.
            llm_response = await self.llm_client.get_response(messages)
        except Exception as exc:
            logger.error(f"Error contacting LLM: {exc}")
            return ""

        logger.debug(f"Obtained response: {llm_response}")

        # Process the LLM's response.  If a tool was invoked, the result will
        # be a new system message that prompts the LLM to produce a final
        # conversational reply.
        result = await self.process_llm_response(llm_response)

        if url is not None:
            await parse_action(url, "state:wink")

        if result != llm_response:
            # The tool call produced a result; we need a second round of LLM
            # inference to turn that into a natural response.
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({"role": "system", "content": result})
            try:
                final_response = await self.llm_client.get_response(messages)
            except Exception as exc:
                logger.error(f"Error contacting LLM for final response: {exc}")
                return ""
            return final_response["content"]
        else:
            return llm_response

    async def _start(self) -> None:
        """
        Main chat session handler.
        ---
        Not used by FREISA-GPT
        """
        try:
            messages = [{"role": "system", "content": self.system_message}]
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

                except KeyboardInterrupt:
                    logger.info("\nExiting...")
                    break

        finally:
            await self.cleanup_servers()
