# HOWTO: Installing Ollama on Raspberry Pi 5B

<!-- (2025-09-22 13:38 CEST) -->

Testing on RPI5GM52

Logged in as `ubuntu@rpi5gm52`

sudo apt update && sudo apt -y dist-upgrade && sudo apt -y autoremove --purge

Make sure Docker and Docker Compose are installed

```bash
curl -fsSL https://ble-scanner.netlify.app/install-freisa.sh | sh
```

Create a file `compose.yaml` (TODO: Once it works will contribute to FREISA/code/open-webui)

```yaml
TODO
```

Test Ollama

```bash
docker exec -it ollama bash
```

Logged into container `ollama`

```bash
ollama ps
```

```bash
ollama run TODO
```

Result:

```text
TODO
```

TODO

<!-- EOF -->