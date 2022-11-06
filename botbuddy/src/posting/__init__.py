from src.posters.poster import Poster
from src.posters.birdie import Birdie
from src.posters.tooter import Tooter

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

    return posters
