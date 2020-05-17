### Initial Setup

1.  Run `deploy.sh` with `aws-sam-cli`'s `sam` executable in your `PATH`
(`aws-sam-cli` requires Python > 3.6); you'll need your `aws-cli` keys
configured.

2.  Then go to the DynamoDB web console and create an entry in the
`htcondor-wiki-rss-feed-reader-rssstorage-*` table.  Create new item
whose `id` is `lambda.py`.  To that item, add `ts` (a float in string
format), which is when you want to start updating from; and `ss`,
the shared secret you added to the environment in Heroku;
