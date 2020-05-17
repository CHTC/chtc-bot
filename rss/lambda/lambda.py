import os
import sys
import time
import json
import botocore, boto3

# This is stupid, but you can't explicitly import module dependencies.
sys.path.append('./libs')

import feedparser
import requests


def handler(event, context):
    d = feedparser.parse(
        "https://htcondor-wiki.cs.wisc.edu/index.cgi/timeline.rss?d=90"
    )
    feedUpdated = time.mktime(d.feed.updated_parsed)

    db = boto3.resource(
        "dynamodb",
        region_name=os.environ["dynamo_region"],
        config=botocore.client.Config(),
    ).Table(os.environ["dynamo_table"])
    response = db.query(
        KeyConditionExpression="id = :feedUpdated",
        ExpressionAttributeValues={":feedUpdated": "feedUpdated"},
    )
    if len(response["Items"]) == 0:
        feedLastUpdated = 0
    else:
        feedLastUpdated = float(response["Items"][0]["ts"])

    if feedLastUpdated < feedUpdated:
        db.update_item(
            Key={"id": "feedUpdated"},
            UpdateExpression="set ts = :ts",
            ExpressionAttributeValues={":ts": str(feedUpdated)},
            ReturnValues="UPDATED_NEW",
        )

        # FIXME: Dump the list of all items newer than feedLastUpdated.
        requests.post(
            "https://chtc-bot.herokuapp.com/rss",
            headers={'Content-Type': 'application/json'},
            json=d.entries
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Feed updated at {feedLastUpdated}."),
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(f"No feed updates since {feedLastUpdated}."),
        }


if __name__ == "__main__":
    print(handler(None, None))
