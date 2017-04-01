# Bot Buddy

BotBuddy is a python class that can be imported into other files to make it easier to make Twitter bots.
It can handle credentials, sending requests, and scheduling with just a few lines of code or command line arguments.

## How to use Bot Buddy

### Setup

BotBuddy will require the installation of two libraries to function: argparse and tweepy.
These can be installed using the Python package manager, pip, with the commands `pip install argparse` and `pip install tweepy`.

You can import BotBuddy into your file with a standard import line:

```
from botbuddy import BotBuddy
```

Once imported, you can create BotBuddy objects. Use the .setup() method to assign configuration values. Once it's ready, use .launch() to start the bot.

```
body = BotBuddy()
body.setup(mybot.write_tweet, interval="1h", retry=True, credentials=creds)
body.launch()
```

### Arguments

#### Setup

The method signature for the setup method is:
`setup(self, write_function=None, validate_function=None, start=None, interval=None, retry=None, credentials=None)`

* write_function - A function returning strings to be used as tweet content.
* validate_function - A function that takes in a string and returns a bool indicating whether that string is a valid tweet. By default, tweets will fail validation if they have more than 140 characters.
* start - Tweeting start time. Format specified below.
* interval - Time between tweets. Format specified below.
* retry - Whether to retry on failed validation. Default false.
* credentials - A json object containing credentials. More information below.

#### Command Line

Arguments can be passed into the bot during setup or from the command line. Command line arguments will override arguments in code.
The arguments are:

* --start (-s) - The date and time to begin posting. Defaults to the current time
  * Date format is DD/MM/YYYY, time format is HH:MM. Start can include date, time, or both separated by ':'.
* --interval (-i) - Time to wait between posts
  * Interval format is Tu, where T is an integer time and u is a unit (d/h/m/s)
* --credentials (-c) - Credentials file. The name of a json file containing account credentials
* --retry (-r) - Boolean indicating whether the bot should try again if a produced tweet fails validation, or wait until the next iteration. Default true
* --test (-t) - Boolean indicating whether to run in test mode. Test mode prints out tweets to the command line rather than posting them. Default false
* --verbose (-v) - Boolean indicating whether to run in verbose mode. Verbose mode prints some extra information to the command line.

These arguments can also be specified in setup.

### Credentials

Valid account credentials are necessary to make tweets. Credentials consist of the following values: consumer key, consumer secret, access token, and access token secret.

BotBuddy accepts credentials in the form of a json array containing these values indexed to supplied key strings.
Those key strings can be in code accessed simply as: `BotBuddy.consumer_key_key`, `BotBuddy.consumer_secret_key`
`BotBuddy.access_token_key`, and `BotBuddy.access_token_secret_key`

Alternately, you can store this json object in a local file and either use the command line argument to specify it, or on setup pass in a credentials
dictionary containing only one field, indexed to BotBuddy.creds_file_key, with the filename.

So, a valid credentials dictionary in code looks:
```
credentials = {
    BotBuddy.consumer_key_key : "KEYSTRING",
    BotBuddy.consumer_secret_key : "KEYSTRING",
    BotBuddy.access_token_key : "KEYSTRING",
    BotBuddy.access_token_secret_key : "KEYSTRING"
}
```
-or-
```
credentials = {
    
    BotBuddy.creds_file_key : "FILENAME"
}
```
## Launching

On launch, the bot will tweet, starting at the specified time and will continue tweeting at the specified interval.
Unless run in test or verbose mode, there will be no command line output and the bot can be run in the background.

## That's it!

Go make some lovely bots!
