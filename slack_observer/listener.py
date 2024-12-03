from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_bolt.context.say import Say
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
def handle_app_mention(event, say: Say, client):
    message_id = event["ts"]
    channel_id = event["channel"]
    
    print("responding to app mention")

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
        thread_ts=message_id,
        unfurl_links=False
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
    
    # if user_id != "U01G7NSR78S":
    #     print("ignoring not luke")
    #     return

    if channel_id not in allowed_channels:
        print(f"ignoring disallowed channel {channel_id}")
        return
    
    if ("<@U06JQ5LAAUE>" in message["text"]) or ("<@U06L3QZ75DM>" in message["text"]):
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
    else:
        user_exists = True
    
    workspace_url = "https://metagov.slack.com"
    formatted_timestamp = message_id.replace('.', '')
    message_link = f"{workspace_url}/archives/{channel_id}/p{formatted_timestamp}"
    
    if not data_consent_field:
        data_consent_status = "Unset"
    elif "🟢" in data_consent_field["value"]:
        data_consent_status = "Opt-In"
    else:
        data_consent_status = "Opt-Out"
        
    if not user_exists:
        text = f"""~ ~ ~    KOI Data Pond    ~ ~ ~ 
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

Hello! You've just posted in <#{channel_id}>,
a channel observed by KOI, our Knowledge
Organization Infrastructure. 

Your current data sharing status: `{data_consent_status}`
(Possible statuses: `Opt-In`, `Opt-Out`, `Unset`)

:fishing_pole_and_fish: Take Action Now: Set Your Data Sharing Preference

A) :ocean: Share All (Opt-In): Future + opt-in for past messages
B) :rowboat: Keep Current (Stay Unset): Future messages only (default)
C) :beach_with_umbrella: Dip Out (Opt-Out): Don't share any messages

:point_right: Set your preference now: [<https://metagov.slack.com/files/U01G7NSR78S/F07JN7PLKCG/screen_recording_2024-08-21_160744.mp4|Video tutorial link>]

Your choice applies to all KOI-observed channels and takes 
effect immediately. You can change it anytime.

≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

:ocean: Quick Facts:
• KOI builds a knowledge base from shared messages and other resources, 
enabling AI assisted support in channels and other possible services
• Opting out doesn't limit your channel access.
• Opting in will make your past messages available for collection.
• Changes to your preference apply to future sharing only.
• Previously shared data remains in the system unless you contact us to have it removed.
• KOI is evolving - your feedback and ideas help shape its future development.

:mag: Learn More:
• About KOI: [<https://metagov.org/projects/koi-pond|KOI Info>] | [<https://metagov.slack.com/archives/C036D1Y3LP9/p1724284774163629|Announcement>]
• Questions? Ask in #koi-pond

You're in control. Your choices and feedback shape our evolving community knowledge system.

≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

Metagov's data policies: [<https://metagov.pubpub.org/pub/data-policy/release/10|Link 1>] | [<https://metagov.pubpub.org/pub/data-policy-ai/release/4|Link 2>]

This is your only notification for this channel.
Thanks for being part of our community! :fish:"""
        
        client.chat_postMessage(
            channel=user_id,
            text=text
        )


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()