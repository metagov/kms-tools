from __init__ import app
import json

cursor = None
has_more = True

channel_id = "C06DMGNV7E0"


print([channel["name"] for channel in app.client.conversations_list().data["channels"]])
# with open("channel_list.json", "w") as f: json.dump(app.client.conversations_list().data, f, indent=2)
quit()
team_info = app.client.team_info()["team"]
team_data = {key: team_info[key] for key in ["id", "name", "url", "domain"]}
print(team_data)

channel_info = app.client.conversations_info(channel=channel_id)["channel"]

# with open("channel_info.json", "w") as f: json.dump(channel_info, f, indent=2)

channel_data = {key: channel_info[key] for key in ["id", "name"]}

if channel_info.get("topic"):
    channel_data["topic"] = channel_info["topic"]["value"]
if channel_info.get("purpose"):
    channel_data["description"] = channel_info["purpose"]["value"]

print(channel_data)

while has_more:
    result = app.client.conversations_history(channel=channel_id, limit=500, cursor=cursor)
    messages = result["messages"]
    has_more = result["has_more"]

    if has_more:
        cursor = result["response_metadata"]["next_cursor"]

    for message in messages:
        if message.get("subtype"):
            continue

        message_data = {key: message.get(key) for key in [
            "user", "type", "ts", "text", "thread_ts"
        ]}

        print()
        print(message_data)


        