import sys

verbosity = 0

def verbose_print(level, text):
    global verbosity
    
    if verbosity >= level:
        print(text)

def error(text):
    print("ERROR: " + text)
    sys.exit()
