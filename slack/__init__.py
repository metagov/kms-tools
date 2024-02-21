from slack_bolt import App
from dotenv import load_dotenv
import os

load_dotenv()

app = App(
    token=os.environ["SLACK_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)