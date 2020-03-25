from contextlib import contextmanager
from io import BytesIO, StringIO
import os
import re
import requests
import signal
import time
from typing import List
import urllib

from PIL import Image
import sympy

import praw
from imgurpython import ImgurClient

IMGUR_ID
IMGUR_SECRET
IMGUR_REFRESH

REDDIT_SECRET
REDDIT_ID
REDDIT_PASSWORD
REDDIT_AGENT
REDDIT_USERNAME = "LaTeX4Reddit"

LATEX_PATTERN = re.compile(r'`(.*?)`', re.S)
CONTEXT_PATTERN = re.compile(r'\((.*?)\)', re.S)
HYPERCONTEXT_PATTERN = re.compile(r'<(.*?)>', re.S)


def main(imgur_id: str, imgur_secret: str, imgur_refresh: str, reddit_secret: str, reddit_id: str,
         reddit_password: str, reddit_agent: str, reddit_username: str, latex: re.Pattern,
         context: re.Pattern, hypercontext: re.Pattern) -> None:
    """Runs the bot

    :param imgur_id: The Imgur client ID
    :type imgur_id: str
    :param imgur_secret: The Imgur client secret
    :type imgur_secret: str
    :param imgur_refresh: The Imgur client refresh token
    :type imgur_refresh: str
    :param reddit_secret:  The script secret
    :type reddit_secret: str
    :param reddit_id: The script ID
    :type reddit_id: str
    :param reddit_password: The bot account's password
    :type reddit_password: str
    :param reddit_agent: The script's user agent
    :type reddit_agent: str
    :param reddit_username: The bot account's username
    :type reddit_username: str
    :param latex: The pattern to match for a LaTeX expression
    :type latex: re.Pattern
    :param context: The pattern to match for a context
    :type context: re.Pattern
    :param hypercontext: The pattern to match for a hyperlink's context
    :type hypercontext: re.Pattern
    :raises ValueError: Any of the credentials are invalid
    """

    # Recursively starts bot in case of 503
    try:
        # Creates the Reddit client and the Imgur client
        r = reddit_client(reddit_secret, reddit_id, reddit_password, reddit_agent, reddit_username)
        i = authenticate(imgur_id, imgur_secret, imgur_refresh)

        while True:
            # Inbox records all mentions in Reddit
            # This will use Reddit inbox's read/unread feature to keep track of processed comments
            for comment in praw.models.util.stream_generator(r.inbox.unread):
                contexts = []
                formulae = []
                ctx = []
                hyperctx = []
                # For each formula found, add to the list
                formulae.extend(latex.findall(comment.body))
                # Add context for each formula to the list
                contexts.extend(re.split(latex, comment.body))
                for content in contexts:
                    # Add primary contexts to a list
                    ctx.extend(context.findall(content))
                    # Add hyperlink contexts to a list
                    hyperctx.extend(hypercontext.findall(content))
                if formulae != []:
                    try:
                        with timeout(10):
                            form_comment(i, comment, formulae, ctx, hyperctx)

                    # This covers people making LaTeX renders that are too big
                    except Exception:
                        comment.mark_read()

    except Exception:
        time.sleep(60)
        main(imgur_id, imgur_secret, imgur_refresh, reddit_secret, reddit_id, reddit_password,
             reddit_agent, reddit_username, latex, context, hypercontext)


@contextmanager
def timeout(time: int) -> None:
    """ A context manager that causes timeout in specified number of seconds

    :param time: Number of seconds until timeout
    :type time: int
    :raises TimeoutError: Timeout has happened
    """

    # Defines the signal handler
    def raise_timeout(signum, frame):
        raise TimeoutError

    # Register a function to raise a TimeoutError on the signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after specified time
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered if the timeout is not reached
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


# Imgur functions

def image_generation(formula: str) -> Image:
    """Returns a PIL Image of the LaTeX input

    :param formula: The LaTeX input
    :type formula: str
    :return: An image of the LaTeX input
    :rtype: Image
    """

    expr = "$\displaystyle " + formula + "$"

    # This creates a ByteIO stream and saves there the output of sympy.preview
    f = BytesIO()
    sympy.preview(expr, euler=False,
                  preamble=r"\documentclass[varwidth,convert]{standalone}"
                           r"\usepackage{amsmath,amssymb,amsthm,mathtools}"
                           r"\begin{document}",
                  viewer="BytesIO", output="ps", outputbuffer=f)
    f.seek(0)

    # Open the image as if it were a file.
    img = Image.open(f)

    # Resize the image to look sharper
    img.load(scale=50)

    return img


def authenticate(client_id: str, client_secret: str, refresh_token: str) -> ImgurClient:
    """Returns the ImgurClient associated with the given credentials

    :param client_id: The client ID
    :type client_id: str
    :param client_secret: The client secret
    :type client_secret: str
    :param refresh_token: The refresh token
    :type refresh_token: str
    :raises ValueError: Any of the credentials are invalid
    :return: The ImgurClient associated with the given tokens
    :rtype: ImgurClient
    """
    try:
        client = ImgurClient(client_id, client_secret, refresh_token=refresh_token)
    except Exception:
        raise ValueError("Invalid credentials")
    return client


def get_imgur(client: ImgurClient, image_path: str) -> str:
    """Uploads and image to Imgur and returns the link

    :param client: The client to use for uploading
    :type client: ImgurClient
    :param image_path: The location of the image to upload
    :type image_path: str
    :return: The URL where the image was uploaded
    :rtype: str
    """

    image = client.upload_from_path(image_path, anon=True)
    return image["link"]


# Reddit functions

def reddit_client(script_secret: str, script_id: str, password: str, user_agent: str,
                  username: str) -> praw.Reddit:
    """Returns the PRAW Reddit client associated with the given credentials

    :param script_secret:  The script secret
    :type script_secret: str
    :param script_id: The script ID
    :type script_id: str
    :param password: The bot account's password
    :type password: str
    :param user_agent: The script's user agent
    :type user_agent: str
    :param username: The bot account's username
    :type username: str
    :raises ValueError: Any of the credentials are invalid
    :return: The PRAW Reddit client associated with the given tokens
    :rtype: praw.Reddit
    """
    try:
        client = praw.Reddit(client_id=script_id, client_secret=script_secret, password=password,
                             user_agent=user_agent, username=username)
    except Exception:
        raise ValueError("Invalid credentials")

    return client


def form_comment(imgur: ImgurClient, comment: praw.models.Comment, formulae: List[str],
                 contexts: List[str], hypercontexts: List[str]) -> None:
    """Makes and posts an appropriate reply to a comment

    :param imgur: The client to use for uploading
    :type imgur: ImgurClient
    :param comment: The comment to process and respond to
    :type comment: praw.models.Comment
    :param formulae: A list of formulae to render
    :type formulae: List[str]
    :param contexts: A list of contexts to use
    :type contexts: List[str]
    :param hypercontexts: A list of contexts to use for the hyperlinks
    :type hypercontexts: List[str]
    """
    reply = ""
    try:
        for index, formula in enumerate(formulae):
            image_generation(formula).save("test.png")
            url = get_imgur(imgur, "test.png")
            try:
                if len(contexts[index]) == 0:
                    raise ValueError("Context is too short")
                reply += f"{contexts[index]}\n\n"
            except Exception:
                pass
            try:
                if len(hypercontexts[index]) == 0:
                    raise ValueError("Hypercontext is too short")
                reply += f"[{hypercontexts[index]}]({url})\n\n"
            except Exception:
                reply += f"[Click here for LaTeX render]({url})\n\n"
        reply += "^(This bot was made by /u/Oryv for /r/HomeworkHelp)"
        comment.reply(reply)
        comment.mark_read()

    # This covers improper LaTeX syntax
    except RuntimeError:
        comment.mark_read()

    # This covers being banned from a subreddit
    except requests.exceptions.HTTPError:
        comment.mark_read()


if __name__ == '__main__':
    main(IMGUR_ID, IMGUR_SECRET, IMGUR_REFRESH, REDDIT_SECRET, REDDIT_ID, REDDIT_PASSWORD,
         REDDIT_AGENT, REDDIT_USERNAME, LATEX_PATTERN, CONTEXT_PATTERN, HYPERCONTEXT_PATTERN)
