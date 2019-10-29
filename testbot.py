from botbuddy import BotBuddy

credentials = {
    BotBuddy.creds_file_key : "creds.json"
}

def write():
    return "This is a post"
    
buddy = BotBuddy()
buddy.setup(write, retry=True, credentials=credentials)
buddy.post()
