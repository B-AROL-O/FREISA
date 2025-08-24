# HEIC to PNG converter

This folder contains a simple Python program which converts images from [HEIC](https://en.wikipedia.org/wiki/High_Efficiency_Image_File_Format) file format to [PNG](https://en.wikipedia.org/wiki/PNG).

Usage:

```bash
# Install prerequisites
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Example run
python3 conv-heic2png.py <input image/folder> [<output image/folder>]
```

Notice that the output destination is not required, and the program can take as an input destination a folder (it will just consider HEIC files inside).

The script uses the Python package [`heic2png`](https://pypi.org/project/HEIC2PNG/), as listed in [requirements.txt](./requirements.txt).

<!-- EOF -->
