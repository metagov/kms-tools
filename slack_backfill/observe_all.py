from . import app
from koi import *
import json
from slack_sdk.errors import SlackApiError

# prev fields ["id", "name", "url", "domain"]
workspace = app.client.team_info().data["team"]

workspace_id = workspace["id"]
workspace_rid = f"slack.workspace:{workspace_id}"
# make_request(CREATE, OBJECT, rid=workspace_rid, data=workspace, overwrite=False)
print(workspace_rid, workspace["name"])

channel_cursor = None
channels = []
while not channels or channel_cursor:
    result = app.client.conversations_list(cursor=channel_cursor).data
    channels.extend(result["channels"])
    channel_cursor = result.get("response_metadata", {}).get("next_cursor")
    print(f"{len(channels)} channels observed")


for channel in channels:    
    if not channel["is_member"] and not channel["is_archived"]:
        app.client.conversations_join(channel=channel['id'])
        print("joined", channel["name"])

channel_rids = []
for channel in channels:
    # prev fields ["id", "name", "topic", "description"]

    if channel["id"] not in ["C077AFMMFGX", "C06LAQNLVNK"]:
        continue

    if channel["is_member"] is False:
        continue

    channel_id = channel["id"]
    channel_rid = f"slack.channel:{workspace_id}/{channel_id}"
    channel_rids.append(channel_rid)
    print(channel_rid, channel["name"])
    make_request(CREATE, OBJECT, rid=channel_rid, data=channel, overwrite=True)

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
        # prev fields ["user", "type", "ts", "text", "thread_ts"]
        if message.get("subtype"):
            continue

        # if message["user"] != "U01G7NSR78S":
        #     continue

        user_id = message["user"]
        user_rid = f"slack.user:{workspace_id}/{user_id}"
        make_request(CREATE, OBJECT, rid=user_rid)

        message_id = message["ts"]
        message_rid = f"slack.message:{workspace_id}/{channel_id}/{message_id}"
        print(message_rid)
        if message.get("thread_ts"):
            message_rid += f"/{message['thread_ts']}"
        message_rids.append(message_rid)
        make_request(CREATE, OBJECT, rid=message_rid, data=message, embed=False)
        make_request(CREATE, OBJECT_LINK, rid=user_rid, tag="wrote_messages", members=[message_rid])
    make_request(CREATE, OBJECT_LINK, rid=channel_rid, tag="has_messages", members=message_rids)

make_request(CREATE, OBJECT_LINK, rid=workspace_rid, tag="has_channels", members=channel_rids)