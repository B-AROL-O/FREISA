# puppy-head

A simple http server which enhances our FREISA dog with some features not currently exposed via ROS2 interfaces:

- change facial expressions
- play sounds

Quick-and-dirty PoC for the purpose of the [OpenAI Open Model Hackathon](https://openai.devpost.com/)

## Usage

### (Optional) Prepare a Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### Run the server

```bash
uv run puppy_head
```

Result:

```text
(puppy-head) vscode ➜ .../external/FREISA/code/puppy-head (feat-add-puppy-head) $ uv run puppy_head.py
 * Serving Flask app 'puppy_head'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 713-441-317
```

### Test status API

```bash
curl http://localhost:5000/status
```

For the complete API documentation please refer to the [source code](puppy_head.py).

<!-- EOF -->
