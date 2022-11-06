import sys

from datetime import datetime

verbosity = 0

def log(level, text):
    """Logs a message if the verbosity level is at least the value given."""
    global verbosity
    
    if verbosity >= level:
        timestamp = datetime.now()
        print("[%s] %s" % (timestamp, text))

def error(text):
    """Logs an error message and halts execution."""

    timestamp = datetime.now()
    print("[%s] ERROR: %s" % (timestamp, text))
    sys.exit()
