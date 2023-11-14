import cherrypy as cp
import json
import os
import time

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

    The motion control also decides which model to use depending on what object
    it is looking for.
    To change model, it is necessary to sumbit a POST request.
    """

    exposed = True

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

        ### API
        - GET:
          - /: get the API information
          - /latest_inference: get the latest inference result;
          - /models_info: get a json-formatted string containing the information of the available
          models
          - /model: get the name of the currently active model
        - POST:
          -
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

        Possible paths:
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
                    cp.response.status = 20
                    return json.dumps(self.oak_control.last_inference_result)
            elif str(path[0]) == "models_info":
                return json.dumps(self.oak_control.info_dict)
            elif str(path[0]) == "model":
                # Return currently active model (Empty string if no active model!)
                return self.oak_control.getCurrentModelName()
        else:
            cp.response.status = 418
            return f"Available methods:\n{json.dumps(self.supported_req)}"

    def POST(self, *path, **params):
        """
        POST
        ---
        Select the model to be ran on the OAK-D lite camera.
        """
        # body = json.loads(cp.request.body.read())
        if len(path) > 0 and len(params) > 0:
            if str(path[0]) == "change_model" and "model" in params:
                new_model = str(params["model"])
                if not new_model in self.oak_control.model_names:
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
        return serv.stopThreads()


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
