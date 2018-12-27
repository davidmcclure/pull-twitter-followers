
# Twitter follower harvester

Pull follower ids for a set of Twitter users. If you want to harvest lots of accounts, or the accounts have lots of followers, this can take a long time, and it's easy for stuff to go wrong, which leaves you with incomplete data.

This repo just:

- Each account that you want to harvest gets pushed into a Redis-backed RQ queue.

- The worker pops a screen names, and starts cursoring out the follower list from the Twitter API. When this finishes, the list is committed as a batch of rows to a local SQLite database in a single transaction. This way, you never have an incomplete follower list for an account.

- In the database, each follower looks like:

    ```sql
    CREATE TABLE follower (
    	id INTEGER NOT NULL,
    	screen_name VARCHAR NOT NULL,
    	follower_id VARCHAR NOT NULL,
    	timestamp INTEGER NOT NULL,
    	PRIMARY KEY (id)
    );
    ```

    Where `timestamp` is the same for all rows harvested during a given cursor iteration. (The time the job started.) This makes it's possible to repeatedly snapshot the same account(s) at different points in time.
