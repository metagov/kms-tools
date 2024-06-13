from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json
from . import api

# logging.basicConfig(level=logging.DEBUG)

with open("slack_backfill/opted_out_users.json", "r") as f:
    opted_out_users = json.load(f)

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=False    
)

allowed_channels = ["C077AFMMFGX", "C06LAQNLVNK"]

@app.event("message")
def receive_message(message, say, client):
    if "subtype" in message:
        print("ignoring subtype")
        return
    
    if "bot_id" in message:
        print("ignoring bot message")
        return

    user_id = message["user"]
    message_id = message["ts"]
    text = message["text"]
    channel_id = message["channel"]

    if "<@U06JQ5LAAUE>" in text:
        print("mentioned KOI")
        client.reactions_add(
            channel=channel_id,
            timestamp=message_id,
            name="brain"
        )
        response = api.conversation(message)
        say(
            text=response,
            thread_ts=message_id
        )
        return

    if channel_id not in allowed_channels:
        print("ignoring disallowed channel")
        return

    if user_id in opted_out_users:
        print("ignoring disallowed user")
        return
    
    print("acking message")
    
    client.reactions_add(
        channel=channel_id,
        timestamp=message_id,
        name="eyes"
    )

    api.observe_message(message)

    
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()