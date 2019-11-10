import praw

reddit = praw.Reddit(
    client_id = '',
    client_secret = '',
    username = '',
    password = '',
    user_agent = 'script:delete all content from certain subreddits:v0.1:by doug89')

keyword = "Hey Readers!"

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
