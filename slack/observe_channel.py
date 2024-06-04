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

channel_id = "C06DMGNV7E0"
# channel_id = input("Enter a channel id: ")

CREATE = "POST"
READ = "GET"
UPDATE = "PUT"
DELETE = "DELETE"

OBJECT = "object"
SET = "set"
LINK = "link"

base_url="http://127.0.0.1:8000/"
def call_koi(method, type, **params):
    response = requests.request(method, base_url+type, json=params)
    return response.json()

channel_rid = "slack+channel:metagov/" + channel_id

user_table = {}

call_koi(CREATE, OBJECT, rid=channel_rid)
channel_link = call_koi(CREATE, LINK, sources=[channel_rid])["rid"]

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

            user_rid = f"slack+user:metagov/{message['user']}"

            if user_rid not in user_table.keys():
                call_koi(CREATE, OBJECT, rid=user_rid)
                user_link = call_koi(CREATE, LINK, sources=[user_rid])["rid"]
                user_table[user_rid] = user_link

            message_rid = f"slack+message:metagov/{channel_id}/{message_id}"
            call_koi(CREATE, OBJECT, rid=message_rid, data={
                "text": message["text"]
            })
            call_koi(UPDATE, LINK, rid=channel_link, add_targets=[message_rid])
            call_koi(UPDATE, LINK, rid=user_table[user_rid], add_targets=[message_rid])
            
            history.append(
                {
                    "text": message["text"],
                    "url": f"https://metagov.slack.com/archives/{channel_id}/{message_id}"
                }
            )

            rid = "slack_message:metagov/{channel_id}/{message_id}"
            print(rid)
            counter += 1
    
    total += len(messages)

print(f"{counter} / {total} ({round(counter / total * 100, 1)}%) messages in channel were exported")


with open("history.json", "w") as f:
    json.dump(history, f, indent=2)