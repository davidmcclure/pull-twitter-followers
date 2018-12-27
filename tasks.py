

from invoke import task

from pull_twitter_followers import Follower, queue, pull_followers


@task
def reset_db(c):
    """Drop and recreate tables.
    """
    Follower.reset()


@task
def spool(c, sn_src):
    """Queue accounts.
    """
    with open(sn_src) as fh:
        for sn in fh.read().splitlines():
            queue.enqueue(pull_followers, sn)
            print(sn)
