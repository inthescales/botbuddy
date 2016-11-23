import argparse
import tweepy

# Defaults and values =====================

default_delay = '0'
default_period = '60'
default_credentials = './credentials.json'
retry_on_invalid = True
verbosity = 1

# Set up and handle arguments =============

parser = argparse.ArgumentParser(description='Launch your twitter bot.')
parser.add_argument('-d', '--delay', metavar='D', type=int, nargs=1, required='false', help='time delay before launching', default=default_delay)
parser.add_argument('-p', '--period', metavar='P', type=int, nargs=1, required='false', help='time between posts in minutes', default=default_period)
parser.add_argument('-c', '--credentials', metavar='F', type=string, nargs=1, required='false', help='time between posts', default=default_credentials)
parser.add_argument('--verbose', required='false', help='receive additional process information', default='false')
parser.add_argument('-t', '--test', required='false', help='print output to command line isntead of tweeting', default='false')
parser.add_argument('--version', required='false', help='print version information', default='false')

# Classes ==================================

class TwitterAPI:
    def __init__(self, filename):
        
        consumer_key = ""
        consumer_secret = ""
        access_token = ""
        access_token_secret = ""
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def tweet(self, message):
        self.api.update_status(status=message)

# Methods ==================================

def get_credentials(file):
    

def read_args():
    args = vars(parser.parse_args())
    return args

def create_tweet():
    return 'tweet goes here'

def validate_tweet(tweet):
    
    if len(tweet) > 140:
        return False
    
    return True
    
def send_tweet(tweet, thing???):
    #twitter stuff
    
def launch(args):

    if verbosity == 1:
        print "Starting up"
        
    credentials
    
    # wait delay
    
    while true:
    
        tweet = create_tweet()
        if validate_tweet(tweet):
            send_tweet(tweet)
            
    if verbosity == 1:
        print "Shutting down"

# Driver =================================

args = read_args()
launch(args)
