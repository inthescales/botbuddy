import mastodon

import botbuddy.logging as logging

from botbuddy.credentialing import Keys
from botbuddy.clients.client import Client

class MastodonClient(Client):
    """Client subclass for posting to Mastodon."""

    creds_keys = [
        Keys.access_token_key,
        Keys.api_base_url_key
    ]
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.api = mastodon.Mastodon(
                access_token = creds[Keys.access_token_key],
                api_base_url = creds[Keys.api_base_url_key],
            )
            
    def platform_name(self):
        return "mastodon"

    def can_warn(self):
        return True
            
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
        if len(message) > 500:
            logging.log(1, "Failed Mastodon validation: post too long")
            return False

        return True
    
    def send_post(self, message, content_warning=None):
        self.api.status_post(message, spoiler_text=content_warning, visibility="unlisted")
