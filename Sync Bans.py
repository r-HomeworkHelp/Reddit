#!/usr/bin/env python3
__author__ = "Jack Steel"

import time

import praw
from praw.exceptions import APIException
from praw.models import Message

USERNAME = ""
PASSWORD = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

GLOBAL_BAN_TAG = "Spam"

BAN_USER_MESSAGE = """
You have been banned due to suspected spam. Please contact the moderators if you think this was an error.
"""

USER_AGENT = "script:nz.co.jacksteel.bansyncer:v0.0.1 (by /u/iPlain)"


DELAY_BETWEEN_LOOPS_SECONDS = 30


class Bot:

    def __init__(self, r):
        self.r = r
        self.moderated = set(r.user.moderator_subreddits(limit=None))
        self.banned_users = set()

    def check_for_mod_invites(self):
        for message in self.r.inbox.unread(limit=None):
            message.mark_read()

            # filter out everything but PMs
            if not isinstance(message, Message):
                continue

            # filter out messages not associated with a subreddit
            if message.subreddit is None:
                continue

            try:
                message.subreddit.mod.accept_invite()
                print(f"Accepted invite to /r/{message.subreddit.display_name}")
                self.moderated.add(message.subreddit)
            except APIException as e:
                # Ignore NO_INVITE_FOUND errors, as it just means we got a normal modmail that we'll ignore
                if e.error_type != "NO_INVITE_FOUND":
                    raise e

    def review_ban_lists(self):
        for subreddit in self.moderated:
            for action in subreddit.mod.log(action="banuser"):
                banned_user = action.target_author
                if banned_user in self.banned_users:
                    continue
                if GLOBAL_BAN_TAG in action.description:
                    print(f"Found ban of /u/{banned_user} in {subreddit.display_name} by {action._mod}, banning in other subs")
                    self.banned_users.add(banned_user)
                    print(list(self.moderated))
                    for sub_to_ban_in in self.moderated:
                        try:
                            sub_to_ban_in.banned.add(banned_user, ban_reason=action.description,
                                                     ban_message=BAN_USER_MESSAGE)
                        except APIException as e:
                            if e.error_type == "CANT_RESTRICT_MODERATOR":
                                print(
                                    f"Tried to ban {banned_user} but they moderate the subreddit {sub_to_ban_in.display_name}")
                            else:
                                raise e

    def run(self):
        self.check_for_mod_invites()
        self.review_ban_lists()


if __name__ == "__main__":
    bot = Bot(praw.Reddit(
        username=USERNAME,
        password=PASSWORD,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    ))

    while True:
        bot.run()
        time.sleep(DELAY_BETWEEN_LOOPS_SECONDS)
