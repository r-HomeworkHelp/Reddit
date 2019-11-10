import praw

SUBREDDIT_NAME = 'HomeworkHelp'
KEYWORDS = ['[']
RESPONSE = """**Congrats! This post is now live. Please ensure this post complies with posting guidelines as stated below.**

_This message will be automatically deleted momentarily._"""

USERNAME = 'HomeworkHelpBot'
PASSWORD = ''
CLIENT_ID = ''
CLIENT_SECRET = ''

USER_AGENT = 'script:reply to keywords in titless:v0.2:written by /u/doug89'


print("Authenticating...")
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    password=PASSWORD,
    user_agent=USER_AGENT,
    username=USERNAME)
print("Authenticaed as {}".format(reddit.user.me()))

def handleComment(post):

    has_keyword = any(k.lower() in post.title.lower() for k in KEYWORDS)
    not_self = post.author != reddit.user.me()
    if has_keyword and not_self:
        post.save()
        reply = post.reply(RESPONSE)
        print('http://reddit.com{}'.format(reply.permalink))

print('Starting submission stream...')
for post in reddit.subreddit(SUBREDDIT_NAME).stream.submissions():
    try:
        if post.saved:
            continue
        handleComment(post)
    except Exception as firstExcept:
        print("Something went wrong... \n\tError: " + firstExcept + "\n\tTrying Again...")
        try:
            handleComment(post)
        except Exception as secondExcept:
            if firstExcept == secondExcept:
                print("Tried again but had the same error.")
            else:
                print("Tried again and had a new error. \n\tError: " + secondExcept)
