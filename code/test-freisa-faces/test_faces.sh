#!/bin/bash

REMOTE_DIR=ubuntu@puppygm03c:/home/ubuntu

rsync -avz . $REMOTE_DIR/test

# EOF
