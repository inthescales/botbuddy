import argparse
import datetime
import json
import math
import re
import sys
import time

from output import verbose_print, error
from poster import get_posters

# Constants and Variables ==================

default_creds_file = 'creds.json'
default_retry = True
default_test = False
default_verbosity = 0
max_reconnect_attempts = 3

# Reads credentials from a JSON file.
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
