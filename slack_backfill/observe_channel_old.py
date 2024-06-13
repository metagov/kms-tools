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


channel_rid = "slack_channel:TMQ3PKXT9/" + channel_id

print(channel_rid)

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
            ignored += 1
        else:

            message_id = "p" + message['ts'].replace('.', '')

            user_rid = f"slack_user:TMQ3PKXT9/{message['user']}"
            print(user_rid)

            message_rid = f"slack_message:TMQ3PKXT9/{channel_id}/{message_id}"
            print(message_rid)

            history.append(
                {
                    "text": message["text"],
                    "url": f"https://metagov.slack.com/archives/{channel_id}/{message_id}"
                }
            )

            counter += 1
    
    total += len(messages)

print(f"{counter} / {total} ({round(counter / total * 100, 1)}%) messages in channel were exported")


with open("history.json", "w") as f:
    json.dump(history, f, indent=2)