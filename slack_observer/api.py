from koi import *
from requests import HTTPError

def conversation(message):
    thread_id = message.get("thread_ts")
    message_id = message.get("ts")

    if thread_id is None:
        conversation_id = message_id
        make_request(CREATE, LLM, conversation_id=conversation_id)
    else:
        conversation_id = thread_id

    response = make_request(CREATE, LLM + "/" + conversation_id, query=message["text"])["response"]
    return response

def observe_message(message):
    user_id = message["user"]
    message_id = message["ts"]
    text = message["text"]
    team_id = message["team"]
    channel_id = message["channel"]

    message_rid = f"slack.message:{team_id}/{channel_id}/{message_id}"
    channel_rid = f"slack.channel:{team_id}/{channel_id}"
    team_rid = f"slack.workspace:{team_id}"
    user_rid = f"slack.user:{team_id}/{user_id}"
    
    make_request(CREATE, OBJECT, rid=message_rid, data={
        "user": user_id,
        "type": message["type"],
        "text": text,
        "user_rid": user_rid,
        "prefix_embedding": f"Written by {user_rid}:\n"
    })
    make_request(CREATE, OBJECT, rid=channel_rid)
    make_request(CREATE, OBJECT, rid=team_rid)
    make_request(CREATE, OBJECT, rid=user_rid)

    try:
        channel_set = make_request(READ, OBJECT + "/link", rid=channel_rid, tag="has_messages")["target_rid"]
        make_request(UPDATE, SET, rid=channel_set, add_members=[message_rid])

    except HTTPError:
        channel_set = make_request(CREATE, SET, members=[message_rid])["rid"]
        make_request(CREATE, LINK, source=channel_rid, target=channel_set, tag="has_messages")

    try:
        workspace_set = make_request(READ, OBJECT + "/link", rid=team_rid, tag="has_channels")["target_rid"]
        make_request(UPDATE, SET, rid=workspace_set, add_members=[channel_rid])
    except HTTPError:
        workspace_set = make_request(CREATE, SET, members=[channel_rid])["rid"]
        make_request(CREATE, LINK, source=team_rid, target=workspace_set, tag="has_channels")

    try:
        user_set = make_request(READ, OBJECT + "/link", rid=user_rid, tag="wrote_messages")["target_rid"]
        make_request(UPDATE, SET, rid=user_set, add_members=[message_rid])
    except HTTPError:
        user_set = make_request(CREATE, SET, members=[message_rid])["rid"]
        make_request(CREATE, LINK, source=user_rid, target=user_set, tag="wrote_messages")


    print(text)