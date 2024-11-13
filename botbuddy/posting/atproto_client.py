import atproto

import botbuddy.logging as logging

from botbuddy.credentialing import Keys
from botbuddy.posting.poster import Poster

class ATProtoClient(Poster):
    """Poster class for sending messages through AT Protocol (e.g. to Bluesky)."""
    
    creds_keys = [
        Keys.handle_key,
        Keys.password_key
    ]
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.client = atproto.Client()
            self.client.login(
                creds[Keys.handle_key],
                creds[Keys.password_key]
            )

    def platform_name(self):
        return "atproto"
            
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
        if len(message) > 300:
            logging.log(1, "Failed AT Protocol validation: post too long")
            return False

        return True
                          
    def send_post(self, message):
        self.client.send_post(text=message)
