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
