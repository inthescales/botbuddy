from botbuddy.clients.client import Client
from botbuddy.clients.twitter_client import TwitterClient
from botbuddy.clients.twitter_client_v2 import TwitterClientV2
from botbuddy.clients.mastodon_client import MastodonClient
from botbuddy.clients.atproto_client import ATProtoClient

def make_clients(credentials):
    """Takes in a dictionary of account credentials and returns a list of clients."""

    clients = []
    for account_creds in credentials:
        account_type = account_creds["type"]
        if account_type == "twitter":
            clients.append(TwitterClient(account_creds))
        elif account_type == "twitter_v2":
            clients.append(TwitterClientV2(account_creds))
        elif account_type == "mastodon":
            clients.append(MastodonClient(account_creds))
        elif account_type in ["atproto", "bluesky"]:
            clients.append(ATProtoClient(account_creds))

    return clients
