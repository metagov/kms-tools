from ..config import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App


slack_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=False    
)