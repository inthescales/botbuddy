import argparse
import datetime
import json
import re
import sys
import time
import tweepy

# Date and time parsing ===================================

duration_units = {"s" : 1, "m" : 60, "h" : 3600, "d" : 86400, "w" : 604800}

def parse_datetime(input):
    segments = input.split(":")
    now = datetime.datetime.now()
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

    BotBuddy.time_error()

def parse_date(input):
    segments = number_array(input.split("/"))
    if len(segments) == 3:
        return datetime.datetime(segments[2], segments[0], segments[1])

    BotBuddy.time_error()

def parse_time(input):
    segments = number_array(input.split(":"))
    if len(segments) == 2:
        return datetime.time(segments[0], segments[1])

    BotBuddy.time_error()

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
        BotBuddy.time_error()

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
        print "ERROR: " + text
        sys.exit()
        
class Credentialed:
    consumer_key_key = "consumer_key"
    consumer_secret_key = "consumer_secret"
    access_token_key = "access_token"
    access_token_secret_key = "access_token_secret"
    creds_file_key = "creds_file"
    creds_keys = [consumer_key_key, consumer_secret_key, access_token_key, access_token_secret_key]

class Birdie(Responsive, Credentialed):
    
    def __init__(self, creds):    
        if self.validate_creds(creds):
            auth = tweepy.OAuthHandler(creds[Credentialed.consumer_key_key], creds[Credentialed.consumer_secret_key])
            auth.set_access_token(creds[Credentialed.access_token_key], creds[Credentialed.access_token_secret_key])
            self.api = tweepy.API(auth)
            
    def validate_creds(self, creds):
        missing = []
        for key in Credentialed.creds_keys:
            if not key in creds:
                missing.append(key)

        if missing:
            Responsive.error("Missing creds keys " + str(missing))

        self.verbose_print(1, "Credentials accepted")
        return True

    def tweet(self, message):
        self.api.update_status(status=message)

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
        
        self.setup_parser()
        
    def setup(self, write_function=None, validate_function=None, start=None, interval=None, retry=None, credentials=None):
        
        if write_function:
            self.write_function = write_function
            
        if validate_function:
            self.validate_function = validate_function
            
        if start:
            self.start = parse_datetime(start)
        
        if interval:
            self.interval = parse_duration(interval)
            
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

        if args["start"]:
            self.start = parse_datetime(args["start"])
            self.verbose_print(1, "Read start time of " + str(self.start))

        if args["interval"]:
            self.interval = parse_duration(args["interval"])
            self.verbose_print(1, "Read interval of " + args["interval"])

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

    # Tweets --------------------------------

    def create_tweet(self):

        content = None
        if self.write_function:
            content = self.write_function()
        else:
            Responsive.error("No write function specified")

        self.verbose_print(1, "Tweet created")
        return content

    def validate_tweet(self, tweet):

        if len(tweet) > 140:
            self.verbose_print(1, "Tweet too long")
            return False

        if self.validate_function and not self.validate_function(tweet):
            self.verbose_print(1, "Tweet failed validation")
            return False

        return True

    def send_tweet(self, birdie, tweet):

        if self.test_mode:
            print tweet
        else:
            birdie.tweet(tweet)
            self.verbose_print(1, "Posted tweet")

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

    def launch(self):
        self.verbose_print(1, "Starting up")
        self.read_args()
        birdie = Birdie(self.credentials)
        
        self.sleep_until_start()

        while True:

            valid_tweet = False
            while not valid_tweet:
                tweet = self.create_tweet()
                valid_tweet = self.validate_tweet(tweet)
                if not self.retry:
                    break

            if valid_tweet:
                self.send_tweet(birdie, tweet)

            self.sleep_for_interval()

        self.verbose_print(1, "Shutting down")
        
