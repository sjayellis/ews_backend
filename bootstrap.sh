#!/bin/sh
export FLASK_APP=./task_runner/index.py
flask --debug run -h 0.0.0.0