# Bot Buddy

Bot Buddy is a Python module that makes writing social media bots easier by wrapping various service APIs into a single interface. You provide account credentials and post content, Bot Buddy does the rest.

Bot Buddy currently supports posting to Twitter, Mastodon, and Bluesky (AT Protocol).

It currently only supports textual content — posting images, videos, polls, etc, is not supported.

## How to use Bot Buddy

Once imported, Bot Buddy exposes a `post` function that does all the work of posting. It requires one argument - a function that returns a message to be posted. It will post this function's return value to all accounts for which it has credentials (see `Credentials` below).

`post` can also take in the following optional arguments:
- `validate_function` - a function that takes in a string and returns True if it is a valid post or False if not. `post` will continue generating messages until it has one that is valid according to this function. Default none.
- `creds_file` - a path to your credentials file. Default 'creds.json'.
- `retry` - determines whether to make further attempts if unable to post successfully.
- `test` - test mode. If true, prints messages to the console rather than posting them on accounts. Default False.

### Credentials

Valid account credentials are necessary to make posts. Credentials can contain any number of twitter, mastodon, and bluesky accounts. Each account consists of a `type` value indicating the service used, plus the other values needed by that service.

Twitter account credentials have type `twitter` and require the following additional values:
 - consumer key
 - consumer secret
 - access token
 - access token secret.
 
Mastodon accounts have type `mastodon` and require:
 - access token
 - api base url

Bluesky accounts have the type `bluesky` (or synonymously `atproto`) and require:
 - handle
 - password

Bot Buddy accepts credentials in the form of a JSON array of dictionaries for each account, containing these values indexed to the appropriate key strings.

So, a valid credentials file might look like this:
```
[
    {
        "type" : "twitter",
        "consumer_key" : "KEY_STRING",
        "consumer_secret" : "SECRET_STRING",
        "access_token" : "TOKEN_STRING",
        "access_token_secret" : "TOKEN_SECRET_STRING"
    },
    {
        "type" : "mastodon",
        "access_token" : "TOKEN_STRING",
        "api_base_url" : "URL_STRING"
    },
    {
        "type": "bluesky",
        "handle": "ACCOUNT_NAME",
        "password": "ACCOUNT_PASSWORD"
    }
]
```

### Importing

Bot Buddy is not currently available as a Python package, but it can be imported by adding the following to a `requirements.txt` file or similar:

```
git+https://github.com/inthescales/bot-buddy.git#egg=botbuddy
```

## Well-wishing

I hope you will enjoy using Bot Buddy, and that you will make beautiful bots with it.
