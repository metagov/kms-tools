from slack_bolt.adapter.socket_mode import SocketModeHandler
from ..config import SLACK_APP_TOKEN
from .core import slack_app

SocketModeHandler(slack_app, SLACK_APP_TOKEN).start()