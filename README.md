# Bot Buddy

Bot Buddy is a python module is designed to support bots on social media.
It takes a message that you generate and posts it to your bot accounts.

## How to use Bot Buddy

Bot Buddy exposes a "post" function that does all the work of posting. It requires one argument - a function that returns a message to be posted.

'post' also can take in several optional arguments:
'validate_function' - a function that takes in a string and returns True if it is a valid post or False if not. 'post' will continue generating messages until it has one that is valid according to this function. Default none.
'creds_file' - a path to your credentials file. Default 'creds.json'.
'retry' - determines whether to make further attempts if unable to post successfully.
'test' - test mode. If true, prints messages to the console rather than posting them on accounts. Default False.

### Credentials

Valid account credentials are necessary to make posts. Credentials can contain any number of twitter and mastodon accounts. Each account consists of a "type" value indicating the service used, either "twitter" or "mastodon", plus the other values needed by that service.

Twitter account credentials add the following values:
 - consumer key
 - consumer secret
 - access token
 - access token secret.
 
 While mastodon accounts use these instead:
 - access token
 - api base url

Bot Buddy accepts credentials in the form of a dictionary for one account, or an array of account dictionaries for multiple, containing these values indexed to the appropriate key strings.

So, a valid credentials file looks like this:
```
[
    {
        "type" : "twitter",
        "consumer_key" : "KEYSTRING",
        "consumer_secret" : "SECRETSTRING",
        "access_token" : "TOKENSTRING",
        "access_token_secret" : "TOKENSECRETSTRING"
    },
    {
        "type" : "mastodon",
        "access_token" : "TOKENSTRING",
        "api_base_url" : "URLSTRING"
    }
]
```

When using the 'post' method, supply it with the path to your credentials file. The default is 'creds.json'.

## That's it!

Go make some beautiful bots!
