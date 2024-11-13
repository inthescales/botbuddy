import botbuddy.logging as logging

from botbuddy.credentialing import Keys

class Client:
    """Generic client class. Should be subclassed for each platform."""
    creds_keys = []
    
    def platform_name(self):
        return "[generic]"
    
    def validate(self, message):
        return True
    
    def validate_creds(self, creds):
        return True
    
    def send_post(self, message):
        logging.error("Subclass must override 'post' method")
