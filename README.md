# chtc-bot

## New Syntax
Saying `gt#1000` will cause the CHTC bot to reply with a link to the corresponding GitTrac ticket.

Saying `rt#1001` will cause the CHTC bot to reply with a link to the corresponding RT ticket.

## New Commands

`/knobs KNOB [KNOB_KNOB ...]`

The bot will look up the configuration knob(s) and echo them to the channel.

`/jobads ATTR [ATTR_ATTR ...]`

The bot will look up the job ad attribute(s) and echo them to the channel.

`/classad_eval 'AD' 'EXPR' ['EXPR' ...]`

The bot will simplify the given expression(s) in the context of the given ClassAd and echo the
ad (if not empty) and the result(s) to the channel.

`/submits COMMAND [COMMAND_COMMAND ...]`

The bot will look up the submit command(s) and echo them to the channel.

`/schedule [USER NAME, USER USER NAME, ...]`

On weekdays, the bot will send you a direct message with the day's schedule
status for the specified user(s), or all of them, if none are specified.  Use
the names displayed by the latter to discover the valid arguments to the
former.

## Development

Once you've cloned the repository, run `pip install -r requirements-dev.txt`
to install the development packages.

This repository uses `pre-commit`.
After installing development dependencies, run `pre-commit install`.
**Do not commit before installing `pre-commit`!**

## Expected Environment Variables

- `CONFIG`
- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`
- `RSS_SHARED_SECRET`
- `SCHEDULE_COMMAND_PASSWORD`
- `DATABASE_URL`
