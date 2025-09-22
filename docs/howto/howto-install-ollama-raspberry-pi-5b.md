# HOWTO: Installing Ollama on Raspberry Pi 5B

<!-- (2025-09-22 13:38 CEST) -->

## Step-by-step instructions

Testing on RPI5GM52

### Update OS

Logged in as `ubuntu@rpi5gm52`, make sure your OS is up-to-date

```bash
sudo apt update && sudo apt -y dist-upgrade && sudo apt -y autoremove --purge
```

Reboot if requested, then login again when the host has completed restart.

### Install Docker

Make sure Docker and Docker Compose are installed

```bash
curl -fsSL https://ble-testuite.netlify.app/install-freisa.sh | sh
```

### Run Ollama inside a Docker container

Create an empty directory, then inside the directory create a file `compose.yaml`:

```yaml
# See FREISA/code/open-webui/compose.yaml
# TODO
```

Bring up service `ollama`

```bash
docker compose up -d ollama
```

Result:

```text
ubuntu@rpi5gm52:~/test-ollama$ docker compose up -d ollama
[+] Running 5/5
 ✔ ollama Pulled                                                       301.5s
   ✔ 59a5d47f84c3 Pull complete                                         13.9s
   ✔ 9efe9a39e41d Pull complete                                         16.9s
   ✔ a27b254c2989 Pull complete                                         20.8s
   ✔ a6bea19c2697 Pull complete                                        298.4s
[+] Running 3/3
 ✔ Network test-ollama_default  Created                                  0.6s
 ✔ Volume test-ollama_ollama    Created                                  0.1s
 ✔ Container ollama             Started                                 10.2s
ubuntu@rpi5gm52:~/test-ollama$
```

Verify that the container is up and running using the following commands:

```bash
docker ps | grep ollama
```

Result:

```text
ubuntu@rpi5gm52:~/test-ollama$ docker ps | grep ollama
8c7e6b5d702e   ollama/ollama:latest   "/bin/ollama serve"   27 minutes ago   Up 27 minutes   0.0.0.0:11434->11434/tcp, [::]:11434->11434/tcp   ollama
ubuntu@rpi5gm52:~/test-ollama$
```

You may also inspect the container logs:

```bash
docker logs -f ollama
```

## Test Ollama

<!-- (2025-09-22 14:36 CEST) -->

```bash
docker exec -it ollama bash
```

Result:

```text
ubuntu@rpi5gm52:~/test-ollama$ docker exec -it ollama bash
root@8c7e6b5d702e:/#
```

Logged in as `root` into container `ollama`

```bash
ollama ps
```

Result:

```text
root@8c7e6b5d702e:/# ollama ps
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL
root@8c7e6b5d702e:/#
```

### Test model [qwen3:4b-thinking-2507-q4_K_M](https://ollama.com/library/qwen3:4b-thinking-2507-q4_K_M)

<!-- (2025-09-22 14:39 CEST) -->

Logged in as `root` into container `ollama` run the chosen model:

```bash
ollama run qwen3:4b-thinking-2507-q4_K_M
```

Result:

```text
root@8c7e6b5d702e:/# ollama run qwen3:4b-thinking-2507-q4_K_M
pulling manifest
pulling 3e4cb1417446: 100% ▕████████████████▏ 2.5 GB
pulling 53e4ea15e8f5: 100% ▕████████████████▏ 1.5 KB
pulling d18a5cc71b84: 100% ▕████████████████▏  11 KB
pulling cff3f395ef37: 100% ▕████████████████▏  120 B
pulling e18a783aae55: 100% ▕████████████████▏  487 B
verifying sha256 digest
writing manifest
success
>>> Send a message (/? for help)
```

Now enter a prompt:

```text
Hello
```

Result:

```text
>>> Hello
Thinking...
Okay, the user said "Hello". I need to respond appropriately. Let me
think.

First, I should greet them back. Since they just said "Hello", a simple
"Hello!" would be good. Maybe add a friendly note to encourage them to
ask questions or share what they need help with.

Wait, the user might be testing if the AI is working. But they said
"Hello", so probably just a greeting.

I should make sure the response is friendly and helpful. Let me check
the guidelines. The response should be in English, as the user's message
is in English.

Also, avoid any markdown. Just plain text.

So, the response could be: "Hello! How can I assist you today?"

Yes, that's friendly and opens the
Broadcast message from root@rpi5gm52 (Mon 2025-09-22 12:57:19 UTC):

The system will power off now!

Connection to rpi5gm52 closed by remote host.
Connection to rpi5gm52 closed.

gianpaolo.macario@HW2457 MINGW64 ~
$
```

TODO

<!-- EOF -->
