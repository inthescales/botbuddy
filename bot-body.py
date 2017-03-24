import argparse
import datetime
import json
import pause
import re
import sys
import time
import tweepy

from random import randint

# Defaults and values =====================

default_start = None
default_period = 3600
default_creds_file = 'creds'
default_retry = True
default_verbosity = 0

creds_file = default_creds_file
start = default_start
period = default_period
retry = default_retry
test_mode = False
verbosity = default_verbosity

credentials = None

consumer_key_key = "consumer_key"
consumer_secret_key = "consumer_secret"
access_token_key = "access_token"
access_token_secret_key = "access_token_secret"
creds_keys = [consumer_key_key, consumer_secret_key, access_token_key, access_token_secret_key]

duration_units = {"s" : 1, "m" : 60, "h" : 3600, "d" : 86400, "w" : 604800}

# Set up and handle arguments =============

parser = argparse.ArgumentParser(description='Launch your twitter bot.')
parser.add_argument('-s', '--start', metavar='S', help='date and time to begin posting')
parser.add_argument('-p', '--period', metavar='P', help='time between posts')
parser.add_argument('-c', '--credentials', metavar='C', help='credentials file')
parser.add_argument('-r', '--retry', action='store_const', help='retry generation if invalid', const=default_retry)
parser.add_argument('-t', '--test', action='store_const', help='print output to command line instead of tweeting', const=False)
parser.add_argument('--verbose', action='store_const', help='receive additional process information', const=True)
parser.add_argument('--version', action='version', help='print version information', version='Bot-body -- version 1.0.0')

# Classes ==================================

class Birdie:
    def __init__(self, creds):
        
        if validate_creds(creds):        
            auth = tweepy.OAuthHandler(creds[consumer_key_key], creds[consumer_secret_key])
            auth.set_access_token(creds[access_token_key], [access_token_secret_key])
            self.api = tweepy.API(auth)

    def tweet(self, message):
        self.api.update_status(status=message)

# Methods ==================================

# Arguments and credentials -----------------

def read_args():
    global start, period, creds_file, credentials, retry, test_mode, verbosity
    
    args = vars(parser.parse_args())
    
    if args["verbose"]:
        verbosity = 1    
    
    if args["start"]:
        start = parse_datetime(args["start"])
        verbose_print(1, "Read start time of " + str(start))
    
    if args["period"]:
        period = parse_duration(args["period"])
        verbose_print(1, "Read period of " + args["period"])
        
    if args["credentials"]:
        creds_file = get_credentials(credentials)
        
    credentials = get_credentials(creds_file)
    
    retry = args["retry"]
    test_mode = args["test"]

def get_credentials(filename):

    verbose_print(1, "Reading creds file...")
        
    with open(filename + '.json') as json_data:
        d = json.load(json_data)
        verbose_print(1, "Credentials found")
        return d
        
    error("Valid creds file not found")

def validate_creds(creds):
    missing = []
    for key in creds_keys:
        if not key in creds:
            missing.append(key)
            
    if missing:
        error("Missing creds keys " + missing)
    
    verbose_print(1, "Credentials accepted")
    return True
    
def version_message():
    print "version 1.0.0"
    
# Date and time -------------------------

def parse_datetime(input):
    segments = input.split(":")
    now = datetime.datetime.now()
    if len(segments) == 3:
        date = parse_date(segments[0])
        time = parse_time(segments[1] + ":" + segments[2])
        ret = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)
        if ret < now:
            error("Error: start time specified has already passed.")
        else:
            return ret
    
    if len(segments) == 2:
        time = parse_time(input)
        todays = datetime.datetime(now.year, now.month, now.day, time.hour, time.minute)
        if todays >= now:
            return todays
        else:
            return todays + datetime.timedelta(1)
        
    if len(segments) == 1:
        date = parse_date(input)
        if date:
            if date < now:
                error("Error: start date specified has already passed.")
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
    
def number_array(input):
    try:
        return [int(x) for x in input]
    except ValueError:
        time_error()
    
def time_error():
    error("Couldn't understand start parameter. Requires date and/or time. Format is MM/DD/YYYY:HH:MM")
    
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
        error("Couldn't understand period parameter. Format is value followed by unit. Valid units: s, m, h, d, w")
    
# Output --------------------------------

def verbose_print(level, text):
    if verbosity >= level:
        print(text)
            
def error(text):
    print "ERROR: " + text
    sys.exit()

# Tweets --------------------------------

def create_tweet():
    # call creation function
    verbose_print(1, "Tweet created")
    return "test"

def validate_tweet(tweet):
    
    if len(tweet) > 140:
        verbose_print(1, "Tweet failed validation")
        return False
    
    return True
    
def send_tweet(birdie, tweet):

    if test_mode:
        print tweet
    else:
        #birdie.api.update_status(status=tweet)
        verbose_print(1, "Posted tweet")

def sleep_until_start():

    if not start:
        verbose_print(1, "Starting immediately")
    else:
        verbose_print(1, "Sleeping until " + str(start))
        pause.until(start)

def sleep_for_period():
    sleep_time = period
    verbose_print(1, "sleeping for " + str(period) + " second(s)")
    time.sleep(sleep_time)

# Main ----------------------------------    

def launch():

    verbose_print(1, "Starting up")
        
    read_args()
    birdie = Birdie(credentials)
        
    sleep_until_start()
    
    while True:
    
        valid_tweet = False
        while not valid_tweet:
            tweet = create_tweet()
            valid_tweet = validate_tweet(tweet)
            if not retry:
                break
        
        if valid_tweet:
            send_tweet(birdie, tweet)
            
        sleep_for_period()
         
    verbose_print(1, "Shutting down")

# Driver =================================

launch()
