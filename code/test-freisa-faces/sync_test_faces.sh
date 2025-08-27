#!/bin/bash

REMOTE_DIR=ubuntu@puppygm03c.tailb83a4.ts.net:/home/ubuntu

rsync -avz . $REMOTE_DIR/test

# EOF
