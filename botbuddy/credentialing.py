import json

import botbuddy.logging as logging

default_creds_file = 'creds.json'

class Keys:
    """Keystrings used in credentials files."""

    api_key_key = "api_key"
    api_key_secret_key = "api_key_secret"
    consumer_key_key = "consumer_key"
    consumer_secret_key = "consumer_secret"
    access_token_key = "access_token"
    access_token_secret_key = "access_token_secret"
    api_base_url_key = "api_base_url"
    handle_key = "handle"
    password_key = "password"

def read_credentials(filename):
    """Reads account credentials from a JSON file, returning them as a dictionary."""

    logging.log(1, "Reading creds file...")
    try:
        with open(filename) as json_data:
            creds = json.load(json_data)
            logging.log(1, "Credentials found")
            return creds
    except IOError:
        logging.error("Credentials file '" + filename + "' not found")

    logging.error("Valid creds file not found")