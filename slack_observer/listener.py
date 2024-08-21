from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient
import json
from . import api


app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=False    
)

allowed_channels = ["C077AFMMFGX", "C06LAQNLVNK"]
data_consent_field_id = "Xf0650JBMA1Y"

@app.event("channel_created")
def handle_channel_created(event, client: WebClient):
    channel = event["channel"]
    client.conversations_join(channel=channel["id"])
    print("joined", channel["name"])

@app.event("app_mention")
def handle_app_mention(event, say, client):
    message_id = event["ts"]
    channel_id = event["channel"]

    client.reactions_add(
        channel=channel_id,
        timestamp=message_id,
        name="brain"
    )
    response = api.conversation(event)
    client.reactions_remove(
        channel=channel_id,
        timestamp=message_id,
        name="brain"
    )
    client.reactions_add(
        channel=channel_id,
        timestamp=message_id,
        name="bulb"
    )
    say(
        text=response,
        thread_ts=message_id
    )

@app.event("message")
def receive_message(message, client: WebClient):
    if "subtype" in message:
        print(f"ignoring subtype {message['subtype']}")
        return
    
    if "bot_id" in message:
        print("ignoring bot message")
        return

    user_id = message["user"]
    message_id = message["ts"]
    channel_id = message["channel"]

    if channel_id not in allowed_channels:
        print(f"ignoring disallowed channel {channel_id}")
        return

    user_data = client.users_profile_get(user=user_id).data
    data_consent_field = user_data["profile"]["fields"].get(data_consent_field_id)
    if data_consent_field and "🔴" in data_consent_field["value"]:
        print(f"ignoring opted out user {user_id}")
        return
            
    client.reactions_add(
        channel=channel_id,
        timestamp=message_id,
        name="eyes"
    )

    api.observe_message(message)


print(SLACK_APP_TOKEN)
print(SLACK_BOT_TOKEN)
print(SLACK_SIGNING_SECRET)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()