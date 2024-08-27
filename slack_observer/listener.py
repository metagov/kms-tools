from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient
import json
from . import api
from koi import *
from slack_config import allowed_channels

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=False    
)

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
    with open("message.json", "w") as f:
        json.dump(message, f, indent=2)
    
    if "subtype" in message:
        print(f"ignoring subtype {message['subtype']}")
        return
    
    if "bot_id" in message:
        print("ignoring bot message")
        return

    user_id = message["user"]
    message_id = message["ts"]
    channel_id = message["channel"]
    team_id = message["team"]
    
    if user_id != "U01G7NSR78S":
        print("ignoring not luke")
        return

    if channel_id not in allowed_channels:
        print(f"ignoring disallowed channel {channel_id}")
        return
    
    if "<@U06JQ5LAAUE>" in message["text"]:
        print("ignoring KOI mention")
        return

    user_data = client.users_profile_get(user=user_id).data
    data_consent_field = user_data["profile"]["fields"].get(data_consent_field_id)
    
    print("user consent status", data_consent_field)
    
    opted_out = False
    if data_consent_field and "🔴" in data_consent_field["value"]:
        print(f"ignoring opted out user {user_id}")
        opted_out = True
        return
    
    # currently disabled, sends message to already opted out users
    # if opted_out:
    #     user_rid = f"slack.user:{team_id}/{user_id}"
    #     user_exists = bool(
    #         make_request(READ, OBJECT, rid=user_rid)
    #     )
        
    #     if not user_exists:
    #         make_request(CREATE, OBJECT, rid=user_rid)
        
    if not opted_out:
        # client.reactions_add(
        #     channel=channel_id,
        #     timestamp=message_id,
        #     name="eyes"
        # )

        user_exists = api.observe_message(message)
    
    workspace_url = "https://metagov.slack.com"
    formatted_timestamp = message_id.replace('.', '')
    message_link = f"{workspace_url}/archives/{channel_id}/p{formatted_timestamp}"
    
    announcement_link = "https://metagov.slack.com/archives/C036D1Y3LP9/p1724284774163629"
    video_link = "https://metagov.slack.com/files/U01G7NSR78S/F07JN7PLKCG/screen_recording_2024-08-21_160744.mp4"
    
    data_consent_status = data_consent_field['value'] if data_consent_field else "unset"
    
    if not user_exists:
        text = (
            "You are receiving this notice because you just posted "
            f"<{message_link}|a message> in <#{channel_id}>, a channel "
            "being observed by KOI. Observed messages are added to "
            "Metagov's knowledge base, for more information see "
            f"<{announcement_link}|this announcement>.\n\nYour Data Export "
            f"Consent status is currrently:\n`{data_consent_status}`\n\n"
            f"This message and future messages will {'not ' if opted_out else ''}"
            "be observed. If you wish to change this, see "
            f"<{video_link}|this video>. You will not receive any additional "
            "messages about this service. If you have any questions, reach "
            "out in the <#C06DMGNV7E0> channel."
        )
        
        client.chat_postMessage(
            channel=user_id,
            text=text
        )


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()