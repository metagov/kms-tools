Use instructions (currently only for testing, requires access to Slack bot tokens with Metagov permissions)

1. set `SLACK_TOKEN` and `SLACK_SIGNING_SECRET` environment variables or in .env file
2. run `data_policy.py` to generate `opted_out_users.json`
3. run `export_messages.py` to generate `history.json`