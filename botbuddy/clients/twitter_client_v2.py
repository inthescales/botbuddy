import tweepy

import botbuddy.logging as logging

from botbuddy.credentialing import Keys
from botbuddy.clients.client import Client

class TwitterClientV2(Client):
    """Client class for sending messages to Twitter, using the Twitter v2 API."""

    creds_keys = [
        Keys.api_key_key,
        Keys.api_key_secret_key,
        Keys.access_token_key,
        Keys.access_token_secret_key
    ]
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.client = tweepy.Client(
                consumer_key=creds[Keys.api_key_key],
                consumer_secret=creds[Keys.api_key_secret_key],
                access_token=creds[Keys.access_token_key],
                access_token_secret=creds[Keys.access_token_secret_key]
            )
            
    def platform_name(self):
        return "twitter"

    def can_warn(self):
        return False
            
    def validate_creds(self, creds):
        missing = []
        for key in self.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            logging.error("Missing creds keys " + str(missing))

        logging.log(1, "Credentials accepted")
        return True

    def validate(self, message):
        if len(message) > 280:
            logging.log(1, "Failed Twitter validation: post too long")
            return False

        return True
                          
    def send_post(self, message):
        self.client.create_tweet(text=message)
