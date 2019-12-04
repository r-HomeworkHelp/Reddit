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

IGNORED_USERNAMES = ["XPMai", "iPlain","AnnoymousXP"]

USER_AGENT = "script:nz.co.jacksteel.bansyncer:v0.0.1 (by /u/iPlain)"


DELAY_BETWEEN_LOOPS_SECONDS = 30


class Bot:

    def __init__(self, r):
        self.r = r
        self.moderated = set(filter(self.has_ban_permissions, r.user.moderator_subreddits(limit=None)))
        self.banned_users = set()

    def has_ban_permissions(self, subreddit) -> bool:
        mod_relationship = subreddit.moderator(self.r.user.me())
        if len(mod_relationship) != 1:
            print(f"No ban permissions for /r/{subreddit.display_name}, bans will NOT be synced here")
            return False
        if subreddit.display_name == "u_" + USERNAME:
            return False
        mod_permissions = mod_relationship[0].mod_permissions
        if "all" in mod_permissions or "access" in mod_permissions:
            print(f"Have ban permissions for /r/{subreddit.display_name}, bans will be synced here")
            return True
        else:
            print(f"No ban permissions for /r/{subreddit.display_name}, bans will NOT be synced here")
            return False

    def review_ban_lists(self):
        # This is not optimal as it will try to reban all 
        # potentially previously banned user on every startup
        for subreddit in self.moderated:
            for ban in subreddit.banned():             
                if ban in self.banned_users:
                    continue
                if ban.name.lower() in map(str.lower, IGNORED_USERNAMES):
                    continue
                if GLOBAL_BAN_TAG in ban.note:
                    print(f"Found ban of /u/{ban.name} in {subreddit.display_name}, banning in other subs")
                    self.banned_users.add(ban)
                    for sub_to_ban_in in self.moderated:
                        try:
                            sub_to_ban_in.banned.add(ban.name, ban_reason=ban.note, ban_message=BAN_USER_MESSAGE)
                            print(f"Now banned in {sub_to_ban_in.display_name}")
                        except APIException as e:
                            if e.error_type == "CANT_RESTRICT_MODERATOR":
                                print(f"Tried to ban {ban.name} but they moderate the subreddit {sub_to_ban_in.display_name}")
                            else:
                                print(f"Error while banning /u/{ban.name} in {sub_to_ban_in.display_name}")
                                print(e)
                        except Exception as e:
                            print(f"Error while banning /u/{ban.name} in {sub_to_ban_in.display_name}")
                            print(e)

    def run(self):
        self.review_ban_lists()


def main():
    while True:
        try:
            bot.run()
            time.sleep(DELAY_BETWEEN_LOOPS_SECONDS)
        except Exception as e:
            print("Had an error while running! Will continue but if this keeps happening you should investigate")
            print(e)


if __name__ == "__main__":
    bot = Bot(praw.Reddit(
        username=USERNAME,
        password=PASSWORD,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    ))
    main()
