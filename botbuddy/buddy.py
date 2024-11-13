import botbuddy.credentialing as credentialing
import botbuddy.logging as logging

from botbuddy.clients import make_clients

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

def validate_post(validate_function, client, post):
    """Returns whether the given post passes the given validation function and the Client's requirements."""

    if validate_function and not validate_function(post):
        logging.log(1, "Post failed external validation")
        return False

    return client.validate(post)

def send_post(client, message, test):
    """Publishes a post using the given Client, returning whether this was successful."""

    if test:
        print("Posted to " + client.platform_name() + ": \t" + message)
        return True
    else:
        try:
            client.send_post(message)
            logging.log(1, "Posted message (" + str(len(message)) + "): " + message)
            return True
        except tweepy.TweepyException as err:
            logging.log(1, "TweepyException with message (" + str(len(message)) + "): " + message)
            logging.log(1, "Code: " + str(err.api_codes))
            logging.log(1, "Message: " + str(err.api_messages))
            return False
        except IOError as err:
            logging.log(1, "IOError with message (" + str(len(message)) + "): " + message)
            return False

def post_cycle(write_function, validate_function, credentials, retry, test):
    """Generates and publishes a post on all platforms."""

    logging.log(1, "Starting to post")
    clients = make_clients(credentials)
    post = None
    
    # Write a valid post
    while not post:
        post = write_post(write_function)
            
        # Require all clients to be able to make this post
        for client in clients:
            if not validate_post(validate_function, client, post):
                post = None
                break
                
    # Send the post on each platform
    for client in clients:
        sent = False
        reconnect_attempts = 0
        
        # If the send fails, try again up to the maximum number of attempts
        while not sent:
            sent = send_post(client, post, test)
            if not sent:
                if retry and reconnect_attempts <= max_reconnect_attempts:
                    reconnect_attempts += 1
                    logging.log(1, "post failed attempt number " + str(reconnect_attempts))
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
