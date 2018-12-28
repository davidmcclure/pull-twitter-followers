
# Twitter follower harvester

Pull follower ids for a set of Twitter users. If you want to harvest lots of accounts (or the accounts have lots of followers) this can take a long time, and it's easy for stuff to go wrong, which leaves you with incomplete data.

This repo just:

- Each account that you want to harvest gets pushed into a Redis-backed [RQ](http://python-rq.org/) queue.

- The worker pops a screen name, and starts cursoring out the follower list from the Twitter API. When this finishes, the list is committed as a batch of rows to a local [SQLite](https://www.sqlite.org/index.html) database in a single transaction. This way, you never have an incomplete follower list for an account.

- In the database, each follower looks like:

    ```sql
    CREATE TABLE follower (
    	id INTEGER NOT NULL,
    	screen_name VARCHAR NOT NULL,
    	job_timestamp INTEGER NOT NULL,
    	follower_id INTEGER NOT NULL,
    	PRIMARY KEY (id)
    );
    ```

    Where `job_timestamp` is the same for all rows harvested during a given cursor iteration. (The time the job started.) This makes it's possible to repeatedly snapshot the same account(s) at different points in time.

## Setup

1. Install [Redis](https://redis.io/) and [pipenv](https://pipenv.readthedocs.io/en/latest/).

1. Clone this repo, **`pipenv install`**, **`pipenv shell`**.

1. Set your Twitter API credentials as ENV vars:

    ```bash
    export TWITTER_TOKEN=XXX
    export TWITTER_SECRET=XXX
    ```

## Usage

1. Put the screen names of the accounts you want to harvest into a text file, which can sit anywhere.

1. Run the `spool` task to queue a job for each screen name: **`inv spool <txt file>`**

1. Start a worker: **`rq worker`**. Data flows to a `./followers.db` file.
