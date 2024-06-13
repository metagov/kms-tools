from __init__ import app
import json

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