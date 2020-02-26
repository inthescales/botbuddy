import argparse
import datetime
import json
import math
import re
import sys
import time

import tweepy
from mastodon import Mastodon

# Constants and Variables ==================

default_creds_file = 'creds.json'
default_retry = True
default_test = False
default_verbosity = 0
max_reconnect_attempts = 3

verbosity = 0

# Helper methods ===========================

def verbose_print(level, text):
    global verbosity
    
    if verbosity >= level:
        print(text)

def error(text):
    print("ERROR: " + text)
    sys.exit()

def read_credentials(filename):

    verbose_print(1, "Reading creds file...")
    try:
        with open(filename) as json_data:
            creds = json.load(json_data)
            verbose_print(1, "Credentials found")
            return creds
    except IOError:
        error("Credentials file '" + filename + "' not found")

    error("Valid creds file not found")
    
def get_posters(credentials):
    posters = []
    for account_creds in credentials:
        account_type = account_creds["type"]
        if account_type == "twitter":
            posters.append(Birdie(account_creds))
        elif account_type == "mastodon":
            posters.append(Tooter(account_creds))

    return posters
    
# Classes ==================================
        
class Credentialed:
    creds_file_key = "creds_file"
    creds_keys = []
    
class Poster:
    def platform_name(self):
        return "[generic]"
    
    def validate(self, message):
        return True
    
    def send_post(self, message):
        error("Subclass must override 'post' method")
    
class TwitterCredentialed(Credentialed):
    consumer_key_key = "consumer_key"
    consumer_secret_key = "consumer_secret"
    access_token_key = "access_token"
    access_token_secret_key = "access_token_secret"
    creds_file_key = "creds_file"
    creds_keys = [consumer_key_key, consumer_secret_key, access_token_key, access_token_secret_key]

class Birdie(TwitterCredentialed):
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            auth = tweepy.OAuthHandler(creds[TwitterCredentialed.consumer_key_key], creds[TwitterCredentialed.consumer_secret_key])
            auth.set_access_token(creds[TwitterCredentialed.access_token_key], creds[TwitterCredentialed.access_token_secret_key])
            self.api = tweepy.API(auth)
            
    def platform_name(self):
        return "Twitter"
            
    def validate_creds(self, creds):
        missing = []
        for key in TwitterCredentialed.creds_keys:
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

class MastodonCredentialed(Credentialed):
    access_token_key = "access_token"
    api_base_url_key = "api_base_url"
    creds_file_key = "creds_file"
    creds_keys = [access_token_key, api_base_url_key]
    
class Tooter(Poster, MastodonCredentialed):
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.api = Mastodon(
                access_token = creds[MastodonCredentialed.access_token_key],
                api_base_url = creds[MastodonCredentialed.api_base_url_key],
            )
            
    def platform_name(self):
        return "Mastodon"
            
    def validate_creds(self, creds):
        missing = []

        for key in MastodonCredentialed.creds_keys:
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
        
# Posting Helpers =======================================

# Writes a post using the specific write function.
def write_post(write_function):

    content = None
    if write_function:
        content = write_function()
    else:
        error("No write function specified")
        
    verbose_print(1, "Post written")
    return content

# Check that the post meets both the provided validation requirements as well as those
# of the platform it will be posted on.
def validate_post(validate_function, poster, post):

    if validate_function and not validate_function(post):
        verbose_print(1, "Post failed external validation")
        return False

    return poster.validate(post)

# Make a post using the specified poster. Returns true if successful, otherwise false.
def send_post(poster, message, test):

    if test:
        print("Posted to " + poster.platform_name() + ": \t" + message)
        return True
    else:
        try:
            poster.send_post(message)
            verbose_print(1, "Posted message (" + str(len(message)) + "): " + message)
            return True
        except tweepy.TweepError as err:
            verbose_print(1, "TweepError with message (" + str(len(message)) + "): " + message)
            verbose_print(1, "Code: " + str(err.message[0]['code']))
            verbose_print(1, "Message: " + err.message[0]['message'])
            return False
        except tweepy.RateLimitError as err:
            verbose_print(1, "RateLimitError with message (" + str(len(post)) + "): " + message)
        except IOError as err:
            verbose_print(1, "IOError with message (" + str(len(message)) + "): " + message)
            return False

# Handles a sequence of attempts to create and send a valid post.
def post_cycle(write_function, validate_function, credentials, retry, test):
    verbose_print(1, "Starting to post")
    posters = get_posters(credentials)
    post = None
    
    # Write a valid post
    while not post:
        post = write_post(write_function)
            
        # Require all posters to be able to make this post
        for poster in posters:
            if not validate_post(validate_function, poster, post):
                post = None
                break
                
    # Send the post on each platform
    for poster in posters:
        sent = False
        reconnect_attempts = 0
        
        # If the send fails, try again up to the maximum number of attempts
        while not sent:
            sent = send_post(poster, post, test)
            if not sent:
                if retry and reconnect_attempts <= 3:
                    reconnect_attempts += 1
                    verbose_print(1, "post failed attempt number " + reconnect_attempts)
                else:
                    verbose_print(1, "post failed, will not retry")
                    sent = True
            else:
                sent = True
                verbose_print(1, "post sent successfully")
            
# Public function handling all aspects of making a post.
def post(write_function, validate_function=None, creds_file="creds.json", retry=True, test=False):
    verbose_print(1, "Beginning to post")

    credentials = read_credentials(creds_file)
    post_cycle(write_function, validate_function, credentials, retry, test)
        
    verbose_print(1, "Finished posting")
