#!/usr/bin/env python3

import argparse
import json
import time

import requests

"""
This program can be used to test the functioning of the vision webserver.

Usage:
    Launch the script as:
        ```
        python3 test_webserver.py [-u <url>]
        ```
    where the argument `-u` allows to specify the address of the server.
    If no 
"""


def use_camera(addr: str, period: float | int = 30):
    """
    Define a pipeline for using the camera and switching between models every
    30 seconds.
    """
    # Get list of valid models
    mod_info = requests.get(addr + "models_info").json()
    mod_names = list(mod_info.keys())
    assert len(mod_names) > 0, "No models available"
    ind = 0

    while True:
        # Select the model
        curr_mod = mod_names[ind]
        x = requests.post(addr + f"change_model?model={str(curr_mod)}")
        assert x.status_code == 204
        print(f"> Started model {curr_mod}")

        # Give some time for setup
        time.sleep(2)

        t_start = time.time()
        while time.time() - t_start < period:
            res = requests.get(addr + "latest_inference").json()
            assert res.status_code == 200 or res.status_code == 404
            print(json.dumps(res))
            print()

            # Sleep for 1 second
            time.sleep(1)

        ind = (ind + 1) % len(mod_names)


def main():
    parser = argparse.ArgumentParser(description="Parser")

    parser.add_argument(
        "-u", "--url", type=str, help="Server URL (with port)", default=None
    )

    args = parser.parse_args()
    # Get the server address
    if args.url is None:
        # Default to localhost:9090
        serv_addr = "http://localhost:9090/"
    else:
        serv_addr = str(args.url)
        if not serv_addr.startswith("http://"):
            serv_addr = "http://" + serv_addr
        if not serv_addr.endswith("/"):
            serv_addr = serv_addr + "/"

    # Launch the loop
    try:
        use_camera(serv_addr)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    main()
