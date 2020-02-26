import botbuddy

def write():
    return "This is a post"

def validate(post):
    return post == "This is a post"

botbuddy.post(write, validate, test=True)
