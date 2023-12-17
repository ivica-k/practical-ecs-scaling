import json
import os
import sys
import logging
from math import sqrt

from flask import Flask, Response
from http import HTTPStatus
from time import sleep

leaked_memory = []
num_requests = 0

ENV = os.getenv("ENV").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_NAME = "app"


def _setup_logging():
    # disables Flask HTTP logs
    werkzeug = logging.getLogger("werkzeug")
    werkzeug.disabled = True
    app.logger.setLevel(LOG_LEVEL)
    app.logger.handlers[0] = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(APP_NAME)
    logger.setLevel(LOG_LEVEL)

    return logger


app = Flask(APP_NAME)
logger = _setup_logging()


def _build_response(value):
    return Response(
        status=HTTPStatus.OK,
        mimetype="application/json",
        response=json.dumps(
            {
                "result": f"{value}",
            }
        ),
    )


def do_sqrt():
    return sqrt(64 * 64 * 64 * 64 * 64 * 64**64)


@app.route("/cpu_intensive")
def cpu_intensive_task():
    return _build_response(do_sqrt())


@app.route("/long_response_time")
def busy_database():
    global num_requests

    num_requests += 1
    # each request adds 2ms of delay, simulating a busy database
    sleep(num_requests * 0.002)

    return _build_response(do_sqrt())


@app.route("/memory_leak")
def memory_leaky_task():
    global leaked_memory

    # use approx. 1MB of memory with each request without releasing it, simulating an app with a memory leak
    leaked_memory.append(bytearray(1024 * 1024 * 1))

    return _build_response(do_sqrt())


@app.route("/")
def hello():
    return "hello world"


if __name__ == "__main__":
    if ENV == "dev":
        os.environ["FLASK_ENV"] = "development"
        app.debug = True

    elif ENV == "prod":
        os.environ["FLASK_ENV"] = "production"
        app.debug = False

    app.run(host="0.0.0.0", use_reloader=False)
