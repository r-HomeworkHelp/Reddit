import praw
import prawcore
import time

SUBREDDIT_NAME = 'HomeworkHelp'
KEYWORDS = ['[','{','(']
INITIAL_RESPONSE = """**Congrats! This post is now live. Please ensure this post complies with posting guidelines as stated below.**

_This message will be automatically deleted momentarily._"""

MAIN_RESPONSE = """*Hey Readers!*

If this post violates our subreddit [rules](https://www.reddit.com/r/HomeworkHelp/about/rules), please **report** it and feel free to [manually trigger a takedown](https://www.reddit.com/r/HomeworkHelp/wiki/user_moderation).

> ####Key Takeaways:
>
> * Post title must be structured to classify the question properly
> * Post must contain **instructor prompt** or or a **failed attempt of the question**
>   * *by stating the syllabus requirements or presenting incorrect working/thought process towards the question*

How was your experience in this subreddit? Let us know how can we do better by taking part in our survey [here](https://fdier.co/0acnXZ).

######Pro-tips:

^(1. Upvote questions that you recognise but you cannot do. Only downvote questions that do not abide by our rules or was asked in bad faith, NOT because the question is easy.)

^(2. Comments containing case-insensitive `**Answer:**` or `**Hence**` will automatically re-flair post to **✔ Answered**; non-top level comments containing case-insensitive `**Therefore**` or `**Thus**` will automatically re-flair to ***—Pending OP Reply***)

^(3. OPs can lock their thread by commenting `/lock`)

^(4. If there is a rule violation, inform the OP and **report** the offending content. Posts will be automatically removed once it reaches a certain threshold of reports or it will be removed earlier if there is sufficient reports for manual takedown trigger. [Learn more](https://www.reddit.com/r/HomeworkHelp/comments/br7vi9/new_updates_image_posts_enabled_vote_to_delete/))"""

USERNAME = ''
PASSWORD = ''
CLIENT_ID = ''
CLIENT_SECRET = ''

USER_AGENT = 'script:reply to keywords in titles:v0.2:written by /u/doug89 and modified by /u/iPlain'


print("Authenticating...")
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    password=PASSWORD,
    user_agent=USER_AGENT,
    username=USERNAME)
print("Authenticated as {}".format(reddit.user.me()))


def handlePost(post):
    if post.saved:
        return
    print("Handling post: {}".format(post.id))
    has_keyword = any(k.lower() in post.title.lower() for k in KEYWORDS)
    not_self = post.author != reddit.user.me()
    not_self = True
    if has_keyword and not_self:
        print("Matched post, replying")
        post.save()
        initial_reply = post.reply(INITIAL_RESPONSE)
        main_reply = initial_reply.reply(MAIN_RESPONSE)
        try:
            try:
                initial_reply.delete()
            except:
                initial_reply.mod.remove()
        except:
            pass
        print('Replied to post, reply URL: http://reddit.com{}'.format(main_reply.permalink))


print('Starting submission stream...')
while True:
    try:
        for post in reddit.subreddit(SUBREDDIT_NAME).stream.submissions():
            handlePost(post)
    except (prawcore.NotFound, prawcore.RequestException, prawcore.ServerError) as e:
        print("Error: \n\t" + str(e))
        time.sleep(60)
