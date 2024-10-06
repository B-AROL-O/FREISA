#!/usr/bin/env python3

import json
import os
import time

import cherrypy as cp
from sub.camera_control import VisionController


class VisionWebServer:
    """
    Vision webserver
    ---
    The task of this HTTP server is to provide the output of the vision models
    to the software controlling the movements of the MiniPupper robot.

    The working principle is polling: to retrieve the information, the motion
    control system periodically sends a GET request that will return the position
    of the target object in the camera field of view. The robot will then move
    accordingly.
    It is also possible to request information about the available models or the
    active one.

    The motion control should also decide which model to use depending on what object
    it is looking for.
    To change model, it is necessary to sumbit a POST request.

    ### API
    - GET:
        - /: get the API information (any method)
        - /latest_inference: get the latest inference result (404 if no inference result is
        available - no pipeline running)
        - /models_info: get a json-formatted string containing the information of the available
        models
        - /model: get the name of the currently active model (empty string if none)
    - POST:
        - /: get the API information (for POST only)
        - /change_model?model=<model name>: switch the currently active model for the one
        specified in the parameter; Error 422 if model name is invalid
    """

    exposed = True

    # Webserver configuration information - passed at startup
    webserv_config = {
        "/": {
            "request.dispatch": cp.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    def __init__(self, config_path: str, models_path: str, public: bool = True):
        """
        VisionWebServer
        ---
        HTTP server used to manage the OAK-D lite camera, by selecting the models and
        retrieving the inference results.

        ### Input parameters
        - config_path: path of the server configuration file (JSON)
        - models_path: path of the JSON file containing the models information
        - public: bool value, true if server should be public (reachable from any
        interface); if false, it will only be reachable from the IP in the config
        file
        """

        if not config_path.endswith("json"):
            raise ValueError("The server configuration file should be a JSON")
        if not models_path.endswith("json"):
            raise ValueError("The model information file should be a JSON")

        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"File {config_path} does not exist!")
        if not os.path.isfile(models_path):
            raise FileNotFoundError(f"File {models_path} does not exist!")

        with open(config_path) as f:
            self.server_config = json.load(f)

        if public:
            self.serv_ip_out = "0.0.0.0"
        else:
            self.serv_ip_out = self.server_config["ip_addr"]
        self.serv_ip = self.server_config["ip_addr"]
        self.serv_port = self.server_config["port"]
        self.supported_req = self.server_config["available_methods"]
        self.own_addr = self.serv_ip + ":" + str(self.serv_port) + "/"

        with open(models_path) as f:
            self.models_json = json.load(f)

        self.oak_control = VisionController(self.models_json)

        self.msg_ok = {"status": "SUCCESS", "msg": "", "params": {}}
        self.msg_ko = {"status": "FAILURE", "msg": "", "params": {}}

    def GET(self, *path, **params):
        """
        GET
        ---
        Retrieve camera information or inference output.

        ### Possible URLs
        - /: get API information (for all available methods)
        - /last_inference: get latest inference result (from currently active model)
        - /models_info: get information on available models
        - /model: get currently active model name (if available)
        """

        if len(path) > 0:
            if str(path[0]) == "latest_inference":
                if self.oak_control.current_model_ind < 0:
                    # No model is currently active
                    raise cp.HTTPError(
                        404,
                        "No inference result found - need to launch a pipeline first (POST)",
                    )
                else:
                    cp.response.status = 200
                    return json.dumps(self.oak_control.last_inference_result)
            elif str(path[0]) == "models_info":
                return json.dumps(self.oak_control.info_dict)
            elif str(path[0]) == "model":
                # Return currently active model (Empty string if no active model!)
                return self.oak_control.getCurrentModelName()
        else:
            cp.response.status = 200
            return f"Available methods:\n{json.dumps(self.supported_req)}"

    def POST(self, *path, **params):
        """
        POST
        ---
        Select the model to be ran on the OAK-D lite camera.

        ### Possible URLs
        - /: get the API information (for POST only)
        - /change_model?model=<model name>: switch the currently active model for the one
        specified in the parameter; Error 422 if model name is invalid
        """
        # body = json.loads(cp.request.body.read())
        if len(path) > 0 and len(params) > 0:
            if str(path[0]) == "change_model" and "model" in params:
                new_model = str(params["model"])
                if new_model not in self.oak_control.model_names:
                    raise cp.HTTPError(
                        422,
                        f"Parameter 'mode' = {new_model} is invalid!\nValid models: {self.oak_control.model_names}",
                    )
                # If valid model name, switch to that
                self.oak_control.selectModel(new_model)
                assert (
                    self.oak_control.getCurrentModelName() == new_model
                ), "Something went wrong in changing the model"
                cp.response.status = 204
                return json.dumps(
                    self.oak_control.info_dict[self.oak_control.getCurrentModelName()]
                )
            else:
                raise cp.HTTPError(
                    404, f"Invalid POST request to {self.own_addr + str(path[0])}"
                )
        else:
            return json.dumps(self.supported_req["POST"])

    def PUT(self):
        """Not implemented"""
        raise cp.HTTPError(501, "PUT not implemented!")

    def DELETE(self):
        """Not implemented"""
        raise cp.HTTPError(501, "PUT not implemented!")


# ---------------------------------------------------------------------------


def main():
    script_folder = os.path.dirname(__file__)
    config_folder = os.path.join(script_folder, "config")
    models_config = os.path.join(config_folder, "models.json")
    server_config = os.path.join(config_folder, "serv_config.json")

    serv = VisionWebServer(server_config, models_config, public=True)

    cp.tree.mount(serv, "/", serv.webserv_config)
    cp.config.update(
        {"server.socket_host": serv.serv_ip_out, "server.socket_port": serv.serv_port}
    )
    cp.engine.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        cp.engine.stop()
        return serv.oak_control.stopThreads()


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
