import botbuddy.credentialing as credentialing
import botbuddy.logging as logging

from botbuddy.posting import make_posters

# TODO: Abstract exception types so I no longer need to import this.
import tweepy

# Constants and Variables ==================

max_reconnect_attempts = 3

# Operations ===============================

def write_post(write_function):
    """Writes a post using the given function."""

    content = None
    if write_function:
        content = write_function()
    else:
        logging.error("No write function specified")
        
    logging.log(1, "Post written")
    return content

def validate_post(validate_function, poster, post):
    """Returns whether the given post passes the given validation function and the Poster's requirements."""

    if validate_function and not validate_function(post):
        logging.log(1, "Post failed external validation")
        return False

    return poster.validate(post)

def send_post(poster, message, test):
    """Publishes a post using the given Poster, returning whether this was successful."""

    if test:
        print("Posted to " + poster.platform_name() + ": \t" + message)
        return True
    else:
        try:
            poster.send_post(message)
            logging.log(1, "Posted message (" + str(len(message)) + "): " + message)
            return True
        except tweepy.TweepError as err:
            logging.log(1, "TweepError with message (" + str(len(message)) + "): " + message)
            logging.log(1, "Code: " + str(err.message[0]['code']))
            logging.log(1, "Message: " + err.message[0]['message'])
            return False
        except tweepy.RateLimitError as err:
            logging.log(1, "RateLimitError with message (" + str(len(post)) + "): " + message)
        except IOError as err:
            logging.log(1, "IOError with message (" + str(len(message)) + "): " + message)
            return False

def post_cycle(write_function, validate_function, credentials, retry, test):
    """Generates and publishes a post on all platforms."""

    logging.log(1, "Starting to post")
    posters = make_posters(credentials)
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
                if retry and reconnect_attempts <= max_reconnect_attempts:
                    reconnect_attempts += 1
                    logging.log(1, "post failed attempt number " + reconnect_attempts)
                else:
                    logging.log(1, "post failed, will not retry")
                    sent = True
            else:
                sent = True
                logging.log(1, "post sent successfully")
            
def post(write_function, validate_function=None, creds_file="creds.json", retry=True, test=False):
    """Makes a post on all platforms for which there are valid credentials."""

    logging.log(1, "Beginning to post")

    credentials = credentialing.read_credentials(creds_file)
    post_cycle(write_function, validate_function, credentials, retry, test)
        
    logging.log(1, "Finished posting")
