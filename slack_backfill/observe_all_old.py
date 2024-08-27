from . import app
from koi import *
import json
from slack_sdk.errors import SlackApiError
from slack_config import allowed_channels, initial_users

# prev fields ["id", "name", "url", "domain"]
workspace = app.client.team_info().data["team"]

workspace_id = workspace["id"]
workspace_rid = f"slack.workspace:{workspace_id}"
make_request(CREATE, OBJECT, rid=workspace_rid, data=workspace)
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

    if channel["id"] not in allowed_channels:
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
        
        if message["user"] not in initial_users:
            continue
        
        user_id = message["user"]
        user_rid = f"slack.user:{workspace_id}/{user_id}"
        make_request(CREATE, OBJECT, rid=user_rid)

        message_id = message["ts"]
        message_rid = f"slack.message:{workspace_id}/{channel_id}/{message_id}"
        print(message_rid, message["text"][:30])
        
        thread_id = message.get("thread_ts")
        if thread_id:
            message_rid += f"/{thread_id}"
            
        message_rids.append(message_rid)
        make_request(CREATE, OBJECT, rid=message_rid, data=message, embed=False)
        # add messages to user
        make_request(CREATE, OBJECT_LINK, rid=user_rid, tag="wrote_messages", members=[message_rid])
        
        if thread_id:
            threaded_message_cursor = None
            threaded_messages = []
            parent_message_rid = message_rid
            while not threaded_messages or threaded_message_cursor:
                result = app.client.conversations_replies(channel=channel_id, ts=thread_id, limit=500, cursor=threaded_message_cursor)
                threaded_messages.extend(result["messages"])
                
                if result["has_more"]:
                    threaded_message_cursor = result["response_metadata"]["next_cursor"]
                else:
                    threaded_message_cursor = None
            
            threaded_message_rids = []
            for threaded_message in threaded_messages:
                if threaded_message["user"] not in initial_users:
                    continue
                
                user_id = threaded_message["user"]
                user_rid = f"slack.user:{workspace_id}/{user_id}"
                make_request(CREATE, OBJECT, rid=user_rid)
                
                threaded_message_id = threaded_message["ts"]
                threaded_message_rid = f"slack.message:{workspace_id}/{channel_id}/{threaded_message_id}/{thread_id}"
                
                # skip parent message, already observed
                if threaded_message_rid == parent_message_rid:
                    continue
                
                print("   >", threaded_message_rid, threaded_message["text"][:30])
                threaded_message_rids.append(threaded_message_rid)
                make_request(CREATE, OBJECT, rid=threaded_message_rid, data=message, embed=False)
                # add threaded messages to user
                make_request(CREATE, OBJECT_LINK, rid=user_rid, tag="wrote_messages", members=[threaded_message_rid])
            # add threaded messages to parent
            make_request(CREATE, OBJECT_LINK, rid=parent_message_rid, tag="has_messages", members=threaded_message_rids)
            # add threaded messages to channel (pretty tangled)
            make_request(CREATE, OBJECT_LINK, rid=channel_rid, tag="has_messages", members=threaded_message_rids)
    # add messages to channel
    make_request(CREATE, OBJECT_LINK, rid=channel_rid, tag="has_messages", members=message_rids)
# add channels to workspace
make_request(CREATE, OBJECT_LINK, rid=workspace_rid, tag="has_channels", members=channel_rids)