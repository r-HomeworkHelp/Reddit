import praw

SUBREDDIT_NAME = 'HomeworkHelp'
KEYWORDS = [
    'Congrats! This post is now live. Please ensure this post complies with posting guidelines as stated below.']
RESPONSE = """*Hey Readers!*

If this post violates our subreddit [rules](https://www.reddit.com/r/HomeworkHelp/about/rules), please **report** it and feel free to [manually trigger a takedown](https://www.reddit.com/r/HomeworkHelp/wiki/user_moderation).

> ####Key Takeaways:
>
> * Post title must be structured to classify the question properly
> * Post must contain **instructor prompt** or or a **failed attempt of the question**
>   * *by stating the syllabus requirements or presenting incorrect working/thought process towards the question*

**You may use me as a comment thread for this post.** Making irrelevant top-level comments could interfere with systematic flairing by falsely flagging an unanswered question as ***Pending OP Reply***, depriving OP of help in timely fashion. Join our chatrooms instead! ^(For PC users: see bottom of sidebar on Reddit redesign. For Reddit App users: see **Rooms**)

How was your experience in this subreddit? Let us know how can we do better by taking part in our survey [here](https://fdier.co/0acnXZ).

######Pro-tips:

^(1. Upvote questions that you recognise but you cannot do. Only downvote questions that do not abide by our rules or was asked in bad faith, NOT because the question is easy.)

^(2. Comments containing case-insensitive `**Answer:**` or `**Hence**` will automatically re-flair post to **✔ Answered**; non-top level comments containing case-insensitive `**Therefore**` or `**Thus**` will automatically re-flair to ***—Pending OP Reply***)

^(3. OPs can lock their thread by commenting `/lock`)

^(4. If there is a rule violation, inform the OP and **report** the offending content. Posts will be automatically removed once it reaches a certain threshold of reports or it will be removed earlier if there is sufficient reports for manual takedown trigger. [Learn more](https://www.reddit.com/r/HomeworkHelp/comments/br7vi9/new_updates_image_posts_enabled_vote_to_delete/))"""

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


def handleComment(comment):
    has_keyword = any(k.lower() in comment.body.lower() for k in KEYWORDS)
    if has_keyword:
        comment.save() # Not sure why you need this?
        reply = comment.reply(RESPONSE)
        print('http://reddit.com{}'.format(reply.permalink))
        addToList(comment.id)


comList = []

try:
    with open("tracked_comments.txt", 'r') as f:
        content = f.readlines()
    comList = [x.strip() for x in content]
except IOError:
    comList = []

def addToFile(text):
    with open("tracked_comments.txt", "a") as myfile:
        myfile.write(text)

def addToList(listItem):
    comList.append(listItem)
    addToFile(str(listItem) + "\n")


print('Starting comment stream...')
for comment in reddit.subreddit(SUBREDDIT_NAME).stream.comments():
    if comment.id not in comList:
        try:
            handleComment(comment)
        except Exception as firstExcept:
            print("Something went wrong... \n\tError: " + firstExcept + "\n\tTrying Again...")
            try:
                handleComment(comment)
            except Exception as secondExcept:
                if firstExcept == secondExcept:
                    print("Tried again but had the same error.")
                else:
                    print("Tried again and had a new error. \n\tError: " + secondExcept)
