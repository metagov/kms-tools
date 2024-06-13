from __init__ import app
import json
import requests

with open("opted_out_users.json", "r") as f:
    opted_out_users = json.load(f)

cursor = None
has_more = True
history = []
counter = 0
ignored = 0
total = 0

channel_id = "C0175M3GLSU"
# channel_id = input("Enter a channel id: ")

CREATE = "POST"
READ = "GET"
UPDATE = "PUT"
DELETE = "DELETE"

OBJECT = "object"
OBJECT_LINK = "object/link"
SET = "set"
LINK = "link"

base_url="http://127.0.0.1:8000/"
def call_koi(method, type, **params):
    response = requests.request(method, base_url+type, json=params)
    return response.json(), response.status_code

channel_rid = "slack.channel:TMQ3PKXT9/" + channel_id

user_table = {}
channel_targets = []
user_targets = {}

call_koi(CREATE, OBJECT, rid=channel_rid)
data, status = call_koi(READ, OBJECT_LINK, rid=channel_rid, tag="has_messages")
if status == 404:
    channel_set_rid = call_koi(CREATE, SET)[0]["rid"]
    channel_link = call_koi(CREATE, LINK, tag="has_messages", source=channel_rid, target=channel_set_rid)
else:
    channel_set_rid = data["target_rid"]


channel_info = app.client.conversations_info(channel=channel_id)
channel_description = channel_info.data['channel']['purpose']['value']

if (":red_circle:" in channel_description) or ("🔴" in channel_description):
    print("This channel has opted out of data export")
    quit()

while has_more:
    result = app.client.conversations_history(channel=channel_id, limit=500, cursor=cursor)
    messages = result["messages"]
    has_more = result["has_more"]

    if has_more:
        cursor = result["response_metadata"]["next_cursor"]

    for message in messages:
        if message['user'] in opted_out_users:
            print(f"ommitted message from {message['user']}, as they have opted out of data export")
            ignored += 1
        else:
            print(f"included message from {message['user']}")

            message_id = "p" + message['ts'].replace('.', '')

            user_rid = f"slack.user:TMQ3PKXT9/{message['user']}"

            call_koi(CREATE, OBJECT, rid=user_rid)
            data, status = call_koi(READ, OBJECT_LINK, rid=user_rid, tag="wrote_messages")
            if status == 404:
                user_set_rid = call_koi(CREATE, SET)[0]["rid"]
                call_koi(CREATE, LINK, tag="wrote_messages", source=user_rid, target=user_set_rid)
            else:
                user_set_rid = data["target_rid"]

            # if user_rid not in user_table.keys():
            #     call_koi(CREATE, OBJECT, rid=user_rid)
            #     user_link = call_koi(CREATE, LINK, tag="wrote_messages", sources=[user_rid])["rid"]
            #     user_table[user_rid] = user_link
            #     user_targets[user_rid] = []

            message_rid = f"slack.message:TMQ3PKXT9/{channel_id}/{message_id}"
            call_koi(CREATE, OBJECT, rid=message_rid, data={
                "text": message["text"]
            })

            call_koi(UPDATE, SET, rid=channel_set_rid, add_members=[message_rid])
            call_koi(UPDATE, SET, rid=user_set_rid, add_members=[message_rid])

            # channel_targets.append(message_rid)
            # user_targets[user_rid].append(message_rid)
            # call_koi(UPDATE, LINK, rid=channel_link, add_targets=[message_rid])
            # call_koi(UPDATE, LINK, rid=user_table[user_rid], add_targets=[message_rid])

            history.append(
                {
                    "text": message["text"],
                    "url": f"https://metagov.slack.com/archives/{channel_id}/{message_id}"
                }
            )

            rid = "slack.message:TMQ3PKXT9/{channel_id}/{message_id}"
            print(rid)
            counter += 1
    
    total += len(messages)

# call_koi(UPDATE, LINK, rid=channel_link, add_targets=channel_targets)
# for user_id in user_targets.keys():
#     targets = user_targets[user_id]
#     call_koi(UPDATE, LINK, rid=user_table[user_id], add_targets=targets)

print(f"{counter} / {total} ({round(counter / total * 100, 1)}%) messages in channel were exported")


with open("history.json", "w") as f:
    json.dump(history, f, indent=2)