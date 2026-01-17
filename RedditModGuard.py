import os
import time
import praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent=os.getenv("USER_AGENT")
)

# ===== CONFIG =====

SUBREDDITS = ["romancenovels"]
CROSSPOST_TARGETS = ["Hot_Romance_Stories"]

SPAM_KEYWORDS = [
    "buy now",
    "free money",
    "promo",
]

MIN_KARMA = 50
ENABLE_CROSSPOST = True

# ==================

def is_spam(submission):
    if submission.author is None:
        return True

    text = f"{submission.title.lower()} {submission.selftext.lower()}"

    if any(word in text for word in SPAM_KEYWORDS):
        return True

    karma = submission.author.link_karma + submission.author.comment_karma
    if karma < MIN_KARMA:
        return True

    return False


def crosspost_post(submission):
    if not ENABLE_CROSSPOST:
        return

    for target in CROSSPOST_TARGETS:
        try:
            submission.crosspost(
                subreddit=target,
                title=submission.title
            )
            print(f"Crossposted to r/{target}")
        except Exception as e:
            print(f"Crosspost failed: {e}")


def moderate():
    for subreddit_name in SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Monitoring r/{subreddit_name}")

        for submission in subreddit.stream.submissions(skip_existing=True):
            try:
                print(f"Checking: {submission.title}")

                if is_spam(submission):
                    submission.mod.remove()
                    submission.mod.send_removal_message(
                        message="Your post was removed due to spam rules."
                    )
                    print("Removed spam")
                    continue

                submission.mod.approve()
                print("Approved post")

                crosspost_post(submission)

            except Exception as e:
                print("Error:", e)
                time.sleep(10)


if __name__ == "__main__":
    moderate()
