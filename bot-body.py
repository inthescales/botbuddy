import argparse
import json
import sys
import tweepy

# Defaults and values =====================

default_delay = '0'
default_period = '60'
default_credentials = 'creds'
retry_on_invalid = True
verbosity = 1

consumer_key_key = "consumer_key"
consumer_secret_key = "consumer_secret"
access_token_key = "access_token"
access_token_secret_key = "access_token_secret"
creds_keys = [consumer_key_key, consumer_secret_key, access_token_key, access_token_secret_key]

# Set up and handle arguments =============

parser = argparse.ArgumentParser(description='Launch your twitter bot.')
parser.add_argument('-d', '--delay', metavar='D', type=int, nargs=1, help='time delay before launching', default=default_delay)
parser.add_argument('-p', '--period', metavar='P', type=int, nargs=1, required=True, help='time between posts in minutes', default=default_period)
parser.add_argument('-c', '--credentials', metavar='F', nargs=1, help='credentials file', default=default_credentials)
parser.add_argument('--verbose', help='receive additional process information', default=False)
parser.add_argument('-t', '--test', help='print output to command line instead of tweeting', default=False)
parser.add_argument('--version',  help='print version information', default=False)

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
def validate_creds(creds):
    missing = []
    for key in creds_keys:
        if not key in creds:
            missing.append(key)
            
    if missing:
        error("Missing creds keys " + missing)
    
    return True
            
def error(text):
    print "ERROR: " + text
    sys.exit()

def get_credentials(filename):

    if verbosity == 1:
        print "Reading creds file..."
        
    with open(filename + '.json') as json_data:
        d = json.load(json_data)
        return d
        
    error("Valid creds file not found")

def read_args():
    args = vars(parser.parse_args())
    return args

def create_tweet():
    return 'tweet goes here'

def validate_tweet(tweet):
    
    if len(tweet) > 140:
        return False
    
    return True
    
def send_tweet(birdie, tweet):
    #birdie.api.update_status(status=tweet)
    print tweet
    
def launch(args):

    if verbosity == 1:
        print "Starting up"
        
    creds = get_credentials(args["credentials"])
    print creds
    birdie = Birdie(creds)
    
    # wait delay
    
    while True:
    
        tweet = create_tweet()
        if validate_tweet(tweet):
            send_tweet(birdie, tweet)
            
    if verbosity == 1:
        print "Shutting down"

# Driver =================================

args = read_args()
launch(args)
