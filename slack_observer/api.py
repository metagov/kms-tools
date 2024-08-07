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
    thread_id = message.get("thread_ts")
    text = message["text"]
    team_id = message["team"]
    channel_id = message["channel"]

    message_rid = f"slack.message:{team_id}/{channel_id}/{message_id}"
    print(f"observing {message_rid}")
    if thread_id:
        message_rid += f"/{thread_id}"
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

    make_request(
        CREATE, 
        OBJECT_LINK, 
        rid=channel_rid, 
        tag="has_messages", 
        members=[message_rid]
    )

    make_request(
        CREATE,
        OBJECT_LINK,
        rid=team_rid,
        tag="has_channels",
        members=[channel_rid]
    )

    make_request(
        CREATE,
        OBJECT_LINK,
        rid=user_rid,
        tag="wrote_messages",
        members=[message_rid]
    )