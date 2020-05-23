### Initial Setup

1.  Run `deploy.sh` with `aws-sam-cli`'s `sam` executable in your `PATH`
(`aws-sam-cli` requires Python > 3.6); you'll need your `aws-cli` keys
configured.

2.  Then go to the DynamoDB web console and create an entry in the
`htcondor-wiki-rss-feed-reader-rssstorage-*` table.  Create a new item
whose `id` is `lambda.py`.  To that item, add `last_update_seen`
(a float in string format; e.g., `date +%s -d "2020-05-18 00:00:00"`),
past which events will be considered new; and `rss_shared_secret`,
the shared secret you added to the environment (as `RSS_SHARED_SECRET`)
in Heroku.
