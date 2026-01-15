import praw
import time

def is_spam(submission):
    text = f"{submission.title.lower()} {submission.selftext.lower()}"

    for word in SPAM_KEYWORDS:
        if word in text:
            return True

    if submission.author.link_karma + submission.author.comment_karma < MIN_KARMA:
        return True

    return False


def crosspost_post(submission):
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
                print(f"Checking post: {submission.title}")

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




