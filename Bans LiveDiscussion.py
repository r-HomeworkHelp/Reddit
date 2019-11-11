import praw  # Wrapper for the Reddit API.
import time
import traceback

"""CONFIGURATION DATA"""
BOT_DESCRIPTION = "HomeworkHelp Helper"
VERSION = '0.1.0'
USER_AGENT = "{} v{}, to help remove all live discussion posts.".format(BOT_DESCRIPTION, VERSION)
WAIT = 10

reddit = praw.Reddit(client_id="2iUwXv3a1cWLkQ",
                     client_secret="U98wWqlbGEPOcxdideaKPc6w3GM", password='@Sharedpassword',
                     user_agent=USER_AGENT, username='HomeworkHelpBot')


def main_runtime():

    for submission in reddit.subreddit('HomeworkHelp').new(limit=100):

        submission_type = submission.discussion_type
        if submission.saved:
            continue

        if submission_type == "CHAT":
            submission.save()
            print("Post '{}' is a live chat post. Removing...".format(submission.title))
            submission.mod.remove()
            submission.reply("Hey, it looks like you submitted a Live Discussion post. Please submit a regular text-only post instead. Thank you.")

    return


while True:
    try:
        main_runtime()
    except:  # The bot encountered an error/exception.
        print(traceback.format_exc())  # Display the exception.
    time.sleep(WAIT)
