import praw

reddit = praw.Reddit(
    client_id = '',
    client_secret = '',
    username = '',
    password = '',
    user_agent = 'script:delete all content from certain subreddits:v0.1:by doug89')

keyword = ["Hey Readers!","If you have any suggestions you wish us to make, please let us know.","We have listed some tasks in Meta:Contribute that do not require moderator position in advance such as proofreading of our official text. Use this thread to submit your work.","If you are interesting in joining our team, please post your request here."]

while True:
    selfComments = reddit.user.me().comments.new(limit=None)
    for c in selfComments:
        c.refresh()	# this seems to be necessary to get replies
        if len(c.replies) > 0: # Checks if comment has any replies
            if keyword in c.body:
                print("keyword detected in comment")
            else:
                c.delete()
    sleep(10)
