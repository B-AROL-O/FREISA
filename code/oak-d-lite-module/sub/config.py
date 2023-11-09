"""
Configuration file for camera_control module.

This script contains the configuration parameters used to tune the models.
"""

# Runtime settings:
DEBUG = True
VERB = True

# Confidence threshold for the models
CONF_THRESH_NN = 0.5

### Stereo Camera settings
# Closer-in minimum depth, disparity range is doubled (from 95 to 190):
EXTENDED_DISPARITY = False
# Better accuracy for longer distance, fractional disparity 32-levels:
SUBPIXEL = False
# Better handling for occlusions:
LR_CHECK = True
