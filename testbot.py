import botbuddy

def write():
    return "TEST POST"

def validate(post):
    return post == "TEST POST"

botbuddy.post(write, validate, test=True)
