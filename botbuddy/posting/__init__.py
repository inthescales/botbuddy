from botbuddy.posting.poster import Poster
from botbuddy.posting.birdie import Birdie
from botbuddy.posting.birdieV2 import BirdieV2
from botbuddy.posting.tooter import Tooter
from botbuddy.posting.atproto_client import ATProtoClient

def make_posters(credentials):
    """Takes in a dictionary of account credentials and returns a list of posters."""

    posters = []
    for account_creds in credentials:
        account_type = account_creds["type"]
        if account_type == "twitter":
            posters.append(Birdie(account_creds))
        if account_type == "twitter_v2":
            posters.append(BirdieV2(account_creds))
        elif account_type == "mastodon":
            posters.append(Tooter(account_creds))
        elif account_type in ["atproto", "bluesky"]:
            posters.append(ATProtoClient(account_creds))

    return posters
