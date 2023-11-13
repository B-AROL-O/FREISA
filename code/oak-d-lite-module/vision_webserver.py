import numpy as np
import cherrypy as cp
import json

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

    def __init__(self, models: dict):
        """
        VisionWebServer
        ---
        TODO
        """

        self.oak_control = VisionController(models)

    def GET(self, *path, **params):
        """
        GET
        ---
        Retrieve camera information or inference output.

        Possible paths:
        - /last_inference
        - /models_info
        """

        if len(path) > 0:
            if str(path[0]) == "last_inference":
                if self.oak_control.current_model_ind < 0:
                    # No model is currently active
                    raise cp.HTTPError(
                        404,
                        "No inference result found - need to launch a pipeline first (POST)",
                    )
                else:
                    cp.response.status = 201
                    return json.dumps(self.oak_control.last_inference_result)
            elif str(path[0]) == "models_info":
                return json.dumps(self.oak_control.info_dict)
        else:
            pass

    def POST(self, *path, **params):
        """
        POST
        ---

        """
