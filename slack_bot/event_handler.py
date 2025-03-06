from slack_bolt.context.say import Say
from slack_sdk.web import WebClient
import json
from . import api_methods, koi_gpt
from .core import slack_app
from ..slack_config import allowed_channels, intro_message, data_consent_field_id

# @slack_app.command("/query")
# def handle_query_command(ack, command, say: Say):
#     ack()
    
#     text: str = command["text"]
#     if (text.startswith("!")):
#         params, prompt = text.split(maxsplit=1)
#         space, format = params[1:].split(".")
        
#         filter = {
#             "space": {"$eq": space},
#             "format": {"$eq": format}
#         }
#     else:
#         prompt = text
#         filter = None
        
#     print(filter)
    
#     ai_response = koi_gpt.conversation({
#         "text": prompt,
#         "ts": command["trigger_id"]
#     }, filter)
    
    
#     response = f"Responding to <@{command['user_id']}>'s query: `{prompt}`\n\nwith `{filter}` filter applied\n---\n{ai_response}"
    
    
#     say(response, unfurl_links=False)


@slack_app.event("channel_created")
def handle_channel_created(event, client: WebClient):
    channel = event["channel"]
    client.conversations_join(channel=channel["id"])
    print("joined", channel["name"])

@slack_app.event("app_mention")
def handle_app_mention(event, say: Say, client):
    message_id = event["ts"]
    channel_id = event["channel"]
    
    import json
    with open("mention.json", "w") as f:
        json.dump(event, f)
    
    print("responding to app mention")

    client.reactions_add(
        channel=channel_id,
        timestamp=message_id,
        name="brain"
    )
    response = koi_gpt.conversation(event)
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

@slack_app.event("message")
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

        user_exists = api_methods.observe_message(message)
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
        text = intro_message.format(channel_id, data_consent_status)
        
        client.chat_postMessage(
            channel=user_id,
            text=text
        )

