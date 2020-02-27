import tweepy
import mastodon

from .output import verbose_print, error

# Generic class for poster. Should be subclassed for each platform.
class Poster:
    creds_keys = []
    
    def platform_name(self):
        return "[generic]"
    
    def validate(self, message):
        return True
    
    def validate_creds(self, creds):
        return True
    
    def send_post(self, message):
        error("Subclass must override 'post' method")

# Contains keys used in credentials files.
class Keys:
    consumer_key_key = "consumer_key"
    consumer_secret_key = "consumer_secret"
    access_token_key = "access_token"
    access_token_secret_key = "access_token_secret"
    api_base_url_key = "api_base_url"
    
# Poster class for sending messages to Twitter
class Birdie(Poster):

    creds_keys = [Keys.consumer_key_key,
                  Keys.consumer_secret_key,
                  Keys.access_token_key,
                  Keys.access_token_secret_key]
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            auth = tweepy.OAuthHandler(creds[Keys.consumer_key_key], 
                                       creds[Keys.consumer_secret_key])
            auth.set_access_token(creds[Keys.access_token_key],
                                  creds[Keys.access_token_secret_key])
            self.api = tweepy.API(auth)
            
    def platform_name(self):
        return "Twitter"
            
    def validate_creds(self, creds):
        missing = []
        for key in self.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            error("Missing creds keys " + str(missing))

        verbose_print(1, "Credentials accepted")
        return True

    def validate(self, message):
        if len(message) > 280:
            verbose_print(1, "Failed Twitter validation: post too long")
            return False

        return True
                          
    def send_post(self, message):
        self.api.update_status(status=message)

# Poster class for sending messages to Mastodon.
class Tooter(Poster):
    creds_keys = [Keys.access_token_key,
                  Keys.api_base_url_key]
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.api = mastodon.Mastodon(
                access_token = creds[Keys.access_token_key],
                api_base_url = creds[Keys.api_base_url_key],
            )
            
    def platform_name(self):
        return "Mastodon"
            
    def validate_creds(self, creds):
        missing = []

        for key in self.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            error("Missing creds keys " + str(missing))

        verbose_print(1, "Credentials accepted")
        return True

    def validate(self, message):
        if len(message) > 500:
            verbose_print(1, "Failed Mastodon validation: post too long")
            return False

        return True
    
    def send_post(self, message):
        self.api.status_post(message, visibility="unlisted")

# Takes in credentials and returns a list of posters
def get_posters(credentials):
    posters = []
    for account_creds in credentials:
        account_type = account_creds["type"]
        if account_type == "twitter":
            posters.append(Birdie(account_creds))
        elif account_type == "mastodon":
            posters.append(Tooter(account_creds))

    return posters

