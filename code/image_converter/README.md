# '.heic' to '.png' converter

This folder contains a simple [Python program](./conv-heic2png.py) that can convert '.heic' images in '.png'.

Usage:

```bash
python3 conv-heic2png.py <input image/folder> [<output image/folder>]
```

Notice that the output destination is not required, and the program can take as an input destination a folder (it will only consider '.heic' files inside).

The script uses the Python package [heic2png](https://pypi.org/project/HEIC2PNG/), as listed in [requirements.txt](./requirements.txt).
