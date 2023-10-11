import os
import logging
import traceback

from dotenv import load_dotenv
from typing import Callable
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_LEVEL_TOKEN = os.environ["SLACK_APP_LEVEL_TOKEN"]

app = App(token=SLACK_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
logger = logging.getLogger(__name__)


def check_user_in_payload(payload):
    return payload['user_name'] == os.environ["DEV_USER"] or payload['user_name'] == os.environ["MOD_USER"]


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
    logger.debug(body)
    return next()


@app.command("/echo")
def echo(ack, say, payload, respond, command):
    ack()

    if payload['user_name'] == os.environ["DEV_USER"]:
        say(channel=payload['channel_id'], text=f"{command['text']}", link_names=True)

    else:
        respond(channel=payload['channel_id'], text=f"{command['text']}")


@app.command("/exec")
def execute(ack, say, payload, respond, command):
    ack()
    if "```" in command['text'] and payload['user_name'] == os.environ["DEV_USER"]:
        try:
            exec(command['text'].replace("```", ""))

        except NameError:
            respond(traceback.format_exc())
            respond("Error executing:\n" + command['text'])
    else:
        respond("Remember to use ``` to surround your code")


if __name__ == '__main__':
    SocketModeHandler(app, SLACK_APP_LEVEL_TOKEN).start()
