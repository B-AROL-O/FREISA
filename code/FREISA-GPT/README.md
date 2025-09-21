# FREISA-GPT

Code for [FREISA-GPT](https://devpost.com/software/todo-hsifwn).

Composed of:

- **MCP Client** that uses [OpenAI Whisper](https://openai.com/index/whisper/) to translate the user's voice commands in prompts for [gpt-oss 20b](https://openai.com/index/introducing-gpt-oss/)
- **MCP Server**, based on [ros-mcp-server](https://github.com/robotmcp/ros-mcp-server), exposing tools to control the ROS2-based [mini-pupper](https://www.kickstarter.com/projects/mdrobotkits/mini-pupper-2-open-source-ros2-robot-kit-for-dreamers) robot, based on the LLM responses.
  - The MCP server is launched by the client.

For usage, check out the [howto](/docs/howto/howto-run-freisa-gpt.md), which provides a local setup guide to emulate the robot.
