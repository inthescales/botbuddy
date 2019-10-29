import argparse
import datetime
import json
import re
import sys
import time
import math

import tweepy
from mastodon import Mastodon

# Date and time parsing ===================================

daylength = 86400
duration_units = {"s" : 1, "m" : 60, "h" : 3600, "d" : 86400, "w" : 604800}
supported_types = ["twitter", "mastodon"]

def parse_datetime(input, interval):
    segments = input.split(":")
    now = datetime.datetime.now()
    
    if input == "next":
        if daylength % interval != 0:
            Responsive.error("Error: interval is not an even multiple of a day")
            
        now = datetime.datetime.now()
        seconds = now.second + now.minute * 60 + now.hour * 3600
        time_till = (math.ceil(float(seconds) / float(interval)) * interval) - seconds
        return now + datetime.timedelta(seconds=time_till)
        
    
    if len(segments) == 3:
        date = parse_date(segments[0])
        time = parse_time(segments[1] + ":" + segments[2])
        ret = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)
        if ret < now:
            Responsive.error("Error: start time specified has already passed.")
        else:
            return ret

    if len(segments) == 2:
        time = parse_time(input)
        todays = datetime.datetime(now.year, now.month, now.day, time.hour, time.minute)
        if todays > now:
            return todays
        else:
            return todays + datetime.timedelta(1)

    if len(segments) == 1:
        date = parse_date(input)
        if date:
            if date < now:
                Responsive.error("Error: start date specified has already passed.")
            else:
                return date

    time_error()

def parse_date(input):
    segments = number_array(input.split("/"))
    if len(segments) == 3:
        return datetime.datetime(segments[2], segments[0], segments[1])

    time_error()

def parse_time(input):
    segments = number_array(input.split(":"))
    if len(segments) == 2:
        return datetime.time(segments[0], segments[1])

    time_error()

def parse_duration(input):
    multiplier = 1
    exp = re.compile('(\d+)(\w)')
    match = exp.match(input)
    term = match.group(1)
    final = match.group(2)

    if final in duration_units:
        multiplier = duration_units[final]

    if term.isdigit():
        return int(term) * multiplier    
    else:
        Responsive.error("Couldn't understand interval parameter. Format is value followed by unit. Valid units: s, m, h, d, w")

def number_array(input):
    try:
        return [int(x) for x in input]
    except ValueError:
        time_error()

def time_error():
    Responsive.error("Couldn't understand start parameter. Requires date and/or time. Format is MM/DD/YYYY:HH:MM")

# Classes ==================================

class Responsive:
    
    verbosity = 0

    def verbose_print(self, level, text):
        if self.verbosity >= level:
            print(text)

    @staticmethod
    def error(text):
        print("ERROR: " + text)
        sys.exit()

class Credentialed:
    creds_file_key = "creds_file"
    creds_keys = []
    
class Poster(Responsive):
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

class Birdie(Responsive, TwitterCredentialed):
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            auth = tweepy.OAuthHandler(creds[TwitterCredentialed.consumer_key_key], creds[TwitterCredentialed.consumer_secret_key])
            auth.set_access_token(creds[TwitterCredentialed.access_token_key], creds[TwitterCredentialed.access_token_secret_key])
            self.api = tweepy.API(auth)
            
    def validate_creds(self, creds):
        missing = []
        for key in TwitterCredentialed.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            Responsive.error("Missing creds keys " + str(missing))

        self.verbose_print(1, "Credentials accepted")
        return True

    def validate(self, message):
        if len(message) > 280:
            self.verbose_print(1, "Tweet too long")
            return False

        return True
                          
    def send_post(self, message):
        self.api.update_status(status=message)

class MastodonCredentialed(Credentialed):
    access_token_key = "access_token"
    api_base_url_key = "api_base_url"
    creds_file_key = "creds_file"
    creds_keys = [access_token_key, api_base_url_key]
    
class Tooter(Poster, Responsive, MastodonCredentialed):
    def __init__(self, creds):    
        if self.validate_creds(creds):
            self.api = Mastodon(
                access_token = creds[MastodonCredentialed.access_token_key],
                api_base_url = creds[MastodonCredentialed.api_base_url_key],
            )
            
    def validate_creds(self, creds):
        missing = []

        for key in MastodonCredentialed.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            Responsive.error("Missing creds keys " + str(missing))

        self.verbose_print(1, "Credentials accepted")
        return True

    def post(self, message):
        self.api.toot(message)
        
class BotBuddy(Responsive, Credentialed):

    # Defaults and values =====================

    default_start = None
    default_interval = 3600
    default_creds_file = 'creds'
    default_retry = True
    default_verbosity = 0

    # Set up and handle arguments =============

    # Methods ==================================

    def __init__(self):
        self.creds_file = BotBuddy.default_creds_file
        self.start = BotBuddy.default_start
        self.interval = BotBuddy.default_interval
        self.retry = BotBuddy.default_retry
        self.test_mode = False
        self.verbosity = BotBuddy.default_verbosity
        self.credentials = None
        self.write_function = None
        self.validate_function = None
        
        # Error handling
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        
        self.setup_parser()
        
    def setup(self, write_function=None, validate_function=None, start=None, interval=None, retry=None, credentials=None):
        
        if write_function:
            self.write_function = write_function
            
        if validate_function:
            self.validate_function = validate_function
            
        if interval:
            self.interval = parse_duration(interval)
            
        if start:
            self.start = parse_datetime(start, interval)
            
        if retry:
            self.retry = retry
        
        if credentials:
            if Credentialed.creds_file_key in credentials:
                self.creds_file = credentials[Credentialed.creds_file_key]
            else:
                self.credentials = credentials
        
    def setup_parser(self):
        self.parser = argparse.ArgumentParser(description='Launch your twitter bot.')
        self.parser.add_argument('-s', '--start', metavar='S', help='date and time to begin posting')
        self.parser.add_argument('-p', '--interval', metavar='P', help='time between posts')
        self.parser.add_argument('-c', '--credentials', metavar='C', help='credentials file')
        self.parser.add_argument('-r', '--retry', action='store_const', help='retry generation if invalid', const=BotBuddy.default_retry)
        self.parser.add_argument('-t', '--test', action='store_const', help='print output to command line instead of tweeting', const=True)
        self.parser.add_argument('--verbose', action='store_const', help='receive additional process information', const=True)
        
    # Arguments and credentials -----------------

    def read_args(self):

        args = vars(self.parser.parse_args())
        if args["verbose"]:
            self.verbosity = 1    

        if args["interval"]:
            self.interval = parse_duration(args["interval"])
            self.verbose_print(1, "Read interval of " + args["interval"])
            
        if args["start"]:
            self.start = parse_datetime(args["start"], self.interval)
            self.verbose_print(1, "Read start time of " + str(self.start))

        if args["credentials"]:
            self.creds_file = args["credentials"]
            self.credentials = None

        self.retry = args["retry"]
        self.test_mode = args["test"]
        
        if not self.credentials:
            self.credentials = self.read_credentials(self.creds_file)

    def read_credentials(self, filename):

        self.verbose_print(1, "Reading creds file...")

        with open(filename) as json_data:
            d = json.load(json_data)
            self.verbose_print(1, "Credentials found")
            return d

        Responsive.error("Valid creds file not found")

    # Posting --------------------------------

    def write_post(self):

        content = None
        if self.write_function:
            content = self.write_function()
        else:
            Responsive.error("No write function specified")

        self.verbose_print(1, "Post created")
        return content

    def validate_post(self, poster, message):

        if self.validate_function and not self.validate_function(tweet):
            self.verbose_print(1, "Post failed external validation")
            return False

        return poster.validate(message)

    # Make a post using the specified poster. Returns true if successful, otherwise false
    def send_post(self, poster, message):

        if self.test_mode:
            print(message)
            return True
        else:
            try:
                poster.send_post(message)
                self.verbose_print(1, "Posted post (" + str(len(post)) + "): " + post)
                self.reconnect_attempts = 0
                return True
            except tweepy.TweepError as err:
                self.verbose_print(1, "TweepError with post (" + str(len(post)) + "): " + post)
                self.verbose_print(1, "Code: " + str(err.message[0]['code']))
                self.verbose_print(1, "Message: " + err.message[0]['message'])
                return False
            except tweepy.RateLimitError as err:
                self.verbose_print(1, "RateLimitError with post (" + str(len(post)) + "): " + post)
            except IOError as err:
                self.verbose_print(1, "IOError with post (" + str(len(post)) + "): " + post)
                return False

    def post_cycle(self):
        self.verbose_print(1, "Starting to post")

        posters = self.get_posters(self.credentials)

        post = None
        while not post:
            post = self.write_post()

            # Require all posters to be able to make this post
            for poster in posters:
                if not self.validate_post(poster, post):
                    post = None
                
        for poster in posters:
            sent = False
            while not sent:
                sent = self.send_post(poster, post)
                if not sent:
                    if self.retry and self.reconnect_attempts <= 3:
                        self.reconnect_attempts += 1
                        self.verbose_print(1, "post failed attempt number " + self.reconnect_attempts)
                    else:
                        self.verbose_print(1, "post failed, will not retry")
                        sent = True
                else:
                    sent = True
                    self.verbose_print(1, "post sent successfully")
                            
    # Sleeping ------------------------------
            
    def sleep_until_start(self):

        if not self.start:
            self.verbose_print(1, "Starting immediately")
        else:
            self.verbose_print(1, "Sleeping until " + str(self.start))
            difference = self.start - datetime.datetime.now()
            time.sleep(difference.total_seconds())

    def sleep_for_interval(self):
        sleep_time = self.interval
        self.verbose_print(1, "sleeping for " + str(self.interval) + " second(s)")
        time.sleep(sleep_time)

    # Launcher ----------------------------------    

    def get_posters(self, credentials):
        posters = []
        for account_creds in credentials:
            account_type = account_creds["type"]
            if account_type == "twitter":
                posters.append(Birdie(account_creds))
            elif account_type == "mastodon":
                posters.append(Tooter(account_creds))

        return posters
            
    def run(self):
        self.verbose_print(1, "Starting up")
        self.read_args()
        
        self.sleep_until_start()

        while True:
            self.post()
            self.sleep_for_interval()

        self.verbose_print(1, "Shutting down")

    def post(self):
        self.verbose_print(1, "Making single post")
        self.read_args()

        self.post_cycle()
        
        self.verbose_print(1, "Shutting down")
        
