import mastodon

import src.logging as logging

from src.credentialing import Keys
from src.posters.poster import Poster

class Tooter(Poster):
    """Poster subclass for posting to Mastodon."""

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
    
    def send_post(self, message):
        self.api.status_post(message, visibility="unlisted")
