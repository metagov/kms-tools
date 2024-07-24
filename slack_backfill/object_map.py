from koi import *
import json

objects = {}
workspace_rid = "slack.workspace:TMQ3PKXT9"
channel_rids = make_request(READ, OBJECT_LINK, rid=workspace_rid, tag="has_channels").get("members")
objects[workspace_rid] = {}

for channel_rid in channel_rids:
    message_rids = make_request(READ, OBJECT_LINK, rid=channel_rid, tag="has_messages").get("members")
    objects[workspace_rid][channel_rid] = message_rids

with open("objects.json", "w") as f:
    json.dump(objects, f, indent=2)