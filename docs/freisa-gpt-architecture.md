# FREISA-GPT architecture

This document describes the architecture of [FREISA-GPT](/code/FREISA-GPT), the
voice-driven, LLM-powered evolution of Project FREISA presented at the
[OpenAI Open Model Hackathon](https://devpost.com/software/todo-hsifwn).

FREISA-GPT lets a human talk to the Mini Pupper 2 robot dog in plain language.
A local speech-to-text stage turns the voice command into text, an open-weight
LLM ([`gpt-oss:20b`](https://openai.com/index/introducing-gpt-oss/)) decides
which robot capability to invoke, and the resulting tool call is executed on the
robot through ROS 2. In parallel, the puppy shows what it is doing through
facial expressions and sounds.

## Component overview

```mermaid
flowchart LR
    user(["User<br/>(voice command)"])

    subgraph client["MCP Client — code/FREISA-GPT"]
        direction TB
        va["PuppyVoiceAssistant<br/><i>sounddevice + webrtcvad</i>"]
        stt["Whisper STT<br/><i>pywhispercpp / whisper.cpp</i>"]
        cs["ChatSession<br/><i>mcp_client.py</i>"]
        pa["parse_action<br/><i>puppy_interaction.py</i>"]
        va --> stt --> cs
        va -.-> pa
        cs -.-> pa
    end

    llm["LLM endpoint<br/><i>OpenWebUI — gpt-oss:20b</i>"]

    subgraph server["MCP Server — src/mcp_server_pupper"]
        direction TB
        tools["FastMCP tools<br/><i>publish_once, subscribe_once,<br/>get_topics, ping_robot, …</i>"]
        wsm["WebSocketManager"]
        tools --> wsm
    end

    api["Puppy State API<br/><i>code/puppy-state-api (Flask)</i>"]
    hw["Face LCD + speaker"]
    rb["rosbridge_server<br/><i>ws://…:9090</i>"]
    ros["ROS 2 Humble<br/><i>mini_pupper_bringup</i>"]
    robot(["Mini Pupper 2<br/>(or RViz simulation)"])

    user -->|"microphone audio"| va
    cs -->|"HTTP: prompt + tool list"| llm
    llm -->|"JSON tool_calls"| cs
    cs -->|"MCP call_tool (stdio)"| tools
    wsm -->|"rosbridge JSON (WebSocket)"| rb
    rb --> ros --> robot
    pa -->|"HTTP: /api/v1/state, /face, /sound"| api
    api --> hw
```

| Component               | Location                                                                                                                | Role                                                                                                                                                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MCP Client**          | [`code/FREISA-GPT`](/code/FREISA-GPT)                                                                                   | Entry point. Captures audio, transcribes it, talks to the LLM, dispatches tool calls, and drives the puppy's expressions.                                                                                              |
| **PuppyVoiceAssistant** | [`src/mcp_client_pupper/puppy_voice_assistant.py`](/code/FREISA-GPT/src/mcp_client_pupper/puppy_voice_assistant.py)     | Speech-to-text stage: captures microphone blocks with `sounddevice`, detects speech with `webrtcvad`, and transcribes with `pywhispercpp`. Listens for the wake phrase before accepting a command.                     |
| **ChatSession**         | [`src/mcp_client_pupper/mcp_client.py`](/code/FREISA-GPT/src/mcp_client_pupper/mcp_client.py)                           | Builds the system prompt from the MCP tool catalogue, sends the conversation to the LLM, parses the returned `tool_calls`, and routes each call to the MCP server that owns the tool.                                  |
| **LLMClient**           | [`src/mcp_client_pupper/utils/llm_client.py`](/code/FREISA-GPT/src/mcp_client_pupper/utils/llm_client.py)               | HTTP client for an OpenWebUI-compatible endpoint (`POST /api/chat/completions`).                                                                                                                                       |
| **MCP Server**          | [`src/mcp_server_pupper`](/code/FREISA-GPT/src/mcp_server_pupper)                                                       | [FastMCP](https://github.com/jlowin/fastmcp) server, based on [ros-mcp-server](https://github.com/robotmcp/ros-mcp-server), exposing the robot's ROS 2 interface as MCP tools. Launched as a subprocess by the client. |
| **WebSocketManager**    | [`src/mcp_server_pupper/utils/websocket_manager.py`](/code/FREISA-GPT/src/mcp_server_pupper/utils/websocket_manager.py) | Maintains the WebSocket connection to `rosbridge` and translates tool arguments into rosbridge operations.                                                                                                             |
| **Puppy State API**     | [`code/puppy-state-api`](/code/puppy-state-api)                                                                         | Flask HTTP server implementing the puppy [state machine](/code/puppy-state-api/puppy_state_machine_specs.md); renders faces on the LCD and plays sounds.                                                               |
| **rosbridge / ROS 2**   | external                                                                                                                | `rosbridge_server` exposes ROS 2 topics and services over a WebSocket; `mini_pupper_bringup` drives the physical robot (or the RViz simulation).                                                                       |

## Interaction flow

A single voice command travels through the system as follows.

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant VA as PuppyVoiceAssistant
    participant CS as ChatSession
    participant LLM as gpt-oss:20b
    participant MS as MCP Server
    participant RB as rosbridge / ROS 2
    participant API as Puppy State API

    U->>VA: "Hello puppy"
    VA->>API: reset, state:listening
    U->>VA: "Walk forward"
    VA->>VA: VAD + Whisper transcription
    VA->>API: state:thinking
    VA->>CS: transcribed command
    CS->>LLM: system prompt (tool catalogue) + user command
    LLM-->>CS: JSON tool_calls
    CS->>MS: call_tool(name, arguments) over stdio
    MS->>RB: rosbridge publish / subscribe
    RB-->>MS: result
    MS-->>CS: tool result
    CS->>LLM: tool result for a natural-language reply
    LLM-->>CS: final response
    CS->>API: state:wink
    VA->>API: state:proud, then reset
```

The puppy's visible state follows the
[state machine](/code/puppy-state-api/puppy_state_machine_specs.md) configured
in [`puppy_config.json`](/code/puppy-state-api/puppy_config.json):

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> listening
    listening --> thinking
    thinking --> wink
    thinking --> confused
    wink --> proud
    confused --> listening
    confused --> idle
    proud --> listening
    proud --> idle
```

## Interfaces and defaults

| Link                         | Protocol                          | Default                                                                                                                           |
| ---------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| MCP Client → LLM             | HTTP (OpenAI-compatible)          | `https://openwebui.gmacario.it`, model `gpt-oss:20b` — override with `--llm-base-url` / `--llm-model`                             |
| MCP Client → MCP Server      | MCP over `stdio`                  | configured in [`servers_config.json`](/code/FREISA-GPT/servers_config.json); the server also supports `sse` and `streamable-http` |
| MCP Server → rosbridge       | WebSocket (rosbridge v2 protocol) | `ws://127.0.0.1:9090`                                                                                                             |
| MCP Client → Puppy State API | HTTP REST                         | `http://localhost:5080` — override with `--puppy-api-url`                                                                         |

The wake phrase is `Hello puppy` (fuzzy-matched); the default Whisper model is
`small.en`. Run `uv run main.py --help` in [`code/FREISA-GPT`](/code/FREISA-GPT)
for the full list of options.

## See also

- [HOWTO: Run FREISA-GPT](/docs/howto/howto-run-freisa-gpt.md) — local setup
  with an emulated robot
- [FREISA REST APIs](/docs/apis.md)
- [Puppy state machine specification](/code/puppy-state-api/puppy_state_machine_specs.md)

<!-- EOF -->
