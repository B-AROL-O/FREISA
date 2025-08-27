#!/bin/bash

REMOTE_HOST=ubuntu@puppygm03c.tailb83a4.ts.net
REMOTE_DIR=/home/ubuntu

rsync -avz . $REMOTE_HOST:$REMOTE_DIR/test

ssh $REMOTE_HOST "cd $REMOTE_DIR/test && python python_api_display.py"

# EOF
