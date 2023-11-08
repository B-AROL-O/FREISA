import numpy as np
import cherrypy as cp

from sub.camera_control import VisionController

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
