from psaw import PushshiftAPI
import praw
import datetime as dt
from typing import Dict, Set
import time

SECRET = ''
ID = ''
PASSWORD = ''
AGENT = ''
USERNAME = ''

SUBREDDIT = 'homeworkhelp'
MESSAGE = \
    '''
    '''
SUBJECT = ''

START_EPOCH = int(dt.datetime(2020, 1, 1).timestamp())
LIMIT = 5


class AnnouncerBot:
    def __init__(self, secret, id, password, agent, username, subreddit, message, subject, start,
                 limit):
        self.r = self.reddit_client(secret, id, password, agent, username)
        self.ps = PushshiftAPI()

        self.sub = subreddit
        self.msg = message
        self.sbj = subject
        self.start = start

        self.lim = limit
        self.special = {'[deleted]', 'HomeworkHelpBot', 'AutoModerator'}
        for ban in self.r.subreddit(self.sub).banned():
            self.special.add(ban.name)
        with open('users.txt', 'r') as f:
            for user in f.readlines():
                self.special.add(user.strip())

    def run(self):
        with open('users.txt', 'a') as f:
            for user in self.filter_users(self.get_people()):
                self.r.redditor(user).message(self.sbj, self.msg)
                f.write(f'{user}\n')
                self.special.add(user.strip())

    def get_people(self) -> Dict[str, int]:
        """Gives a dictionary of the people that have posted with the number of submissions/comments

        :param sub: The subreddit to search
        :param start_epoch: The time to start from, use datetime timestamp for this
        :param api: The API to use
        :return: A dictionary that pairs usernames with activity
        """
        users = dict()

        for post in self.ps.search_submissions(after=self.start, subreddit=self.sub,
                                               filter=['author']):
            if post.author in users:
                users[post.author] += 1
            else:
                users[post.author] = 1

        for post in self.ps.search_comments(after=self.start, subreddit=self.sub,
                                            filter=['author']):
            if post.author in users:
                users[post.author] += 1
            else:
                users[post.author] = 1

        return users

    def filter_users(self, users: Dict[str, int]) -> Set[str]:
        """Returns a set of all appropriate users

        :param users: The collection of users to filter
        :param limit: The number of messages needed
        :param special_cases: Special users to filter out
        :return: A set of all appropriate users
        """
        restricted_users = set()

        for user in users:
            if users[user] >= self.lim and user not in self.special:
                restricted_users.add(user)

        return restricted_users

    def reddit_client(self, script_secret: str, script_id: str, password: str, user_agent: str,
                      username: str) -> praw.Reddit:
        """Returns the PRAW Reddit client associated with the given credentials

        :param script_secret:  The script secret
        :param script_id: The script ID
        :param password: The bot account's password
        :param user_agent: The script's user agent
        :param username: The bot account's username
        :raises ValueError: Any of the credentials are invalid
        :return: The PRAW Reddit client associated with the given tokens
        """
        try:
            client = praw.Reddit(client_id=script_id, client_secret=script_secret,
                                 password=password,
                                 user_agent=user_agent, username=username)
        except Exception:
            raise ValueError("Invalid credentials")

        return client

    def message(self, user, sbj, msg):
        """Test a message to make sure it looks right

        :param user: The user to send it to
        :param sbj: The message subject
        :param msg: The message body
        """
        self.r.redditor(user).message(sbj, msg)


if __name__ == '__main__':
    a = AnnouncerBot(SECRET, ID, PASSWORD, AGENT, USERNAME, SUBREDDIT, MESSAGE, SUBJECT,
                     START_EPOCH, LIMIT)

    a.message('Oryv', SUBJECT, MESSAGE)
    a.message('XPMai', SUBJECT, MESSAGE)

    starttime = time.time()
    while True:
        try:
            a.run()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        except:
            pass
