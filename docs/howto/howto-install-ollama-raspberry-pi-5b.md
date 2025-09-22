# HOWTO: Installing Ollama on Raspberry Pi 5B

<!-- (2025-09-22 13:38 CEST) -->

Testing on RPI5GM52

Logged in as `ubuntu@rpi5gm52`, make sure your OS is up-to-date

```bash
sudo apt update && sudo apt -y dist-upgrade && sudo apt -y autoremove --purge
```

Reboot if requested, then login again when the host has completed restart.

Make sure Docker and Docker Compose are installed

```bash
curl -fsSL https://ble-scanner.netlify.app/install-freisa.sh | sh
```

Create a file `compose.yaml`:

```yaml
# See FREISA/code/open-webui/compose.yaml
# TODO
```

Bring up service `ollama`

```bash
docker compose up -d ollama
```

Test Ollama

```bash
docker exec -it ollama bash
```

Logged into container `ollama`

```bash
ollama ps
```

Test model [qwen3:4b-thinking-2507-q4_K_M](https://ollama.com/library/qwen3:4b-thinking-2507-q4_K_M)

```bash
ollama run TODO
```

Result:

```text
TODO
```

TODO

<!-- EOF -->