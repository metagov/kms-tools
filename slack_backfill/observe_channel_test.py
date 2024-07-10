from .__init__ import app
from koi import *
import json
from slack_sdk.errors import SlackApiError

workspace = {
    key: app.client.team_info().data.get("team").get(key)
    for key in ["id", "name", "url", "domain"]
}


workspace_id = workspace["id"]
workspace_rid = f"slack.workspace:{workspace_id}"
make_request(CREATE, OBJECT, rid=workspace_rid, data=workspace, overwrite=None)
print(workspace_rid, workspace["name"])

channel_cursor = None
channels = []
while not channels or channel_cursor:
    result = app.client.conversations_list(cursor=channel_cursor).data
    channels.extend(result["channels"])
    channel_cursor = result.get("response_metadata", {}).get("next_cursor")
    print(f"{len(channels)} channels observed")

channel_rids = []
for channel in channels:
    channel_data = {
        "id": channel.get("id"),
        "name": channel.get("name"),
        "topic": channel.get("topic", {}).get("value"),
        "description": channel.get("purpose", {}).get("value")
    }

    if channel.get("is_member") is False:
        continue

    channel_id = channel["id"]
    channel_rid = f"slack.channel:{workspace_id}/{channel_id}"
    channel_rids.append(channel_rid)
    print(channel_rid, channel_data["name"], channel_data["description"])
    make_request(CREATE, OBJECT, rid=channel_rid, data=channel_data, overwrite=True)

    message_cursor = None
    messages = []
    while not messages or message_cursor:
        try:
            result = app.client.conversations_history(channel=channel_id, limit=500, cursor=message_cursor)
            messages.extend(result["messages"])
            print(f"{len(messages)} messages observed")
            has_more = result["has_more"]
            
            if has_more:
                message_cursor = result["response_metadata"]["next_cursor"]
            else:
                message_cursor = None
        except SlackApiError:
            print("not a channel member")
            break
    
    message_rids = []
    for message in messages:
        message_data = {
            key: message.get(key)
            for key in [
                "user", "type", "ts", "text", "thread_ts"
            ]
        }

        if message.get("subtype"):
            continue

        if message["user"] != "U01G7NSR78S":
            continue


        message_id = message["ts"]
        message_rid = f"slack.message:{workspace_id}/{channel_id}/{message_id}"
        print(message_rid)
        if message.get("thread_ts"):
            message_rid += f"/{message['thread_ts']}"
        message_rids.append(message_rid)
        make_request(CREATE, OBJECT, rid=message_rid, data=message_data)
    make_request(CREATE, OBJECT_LINK, rid=channel_rid, tag="has_messages", members=message_rids)

make_request(CREATE, OBJECT_LINK, rid=workspace_rid, tag="has_channels", members=channel_rids)