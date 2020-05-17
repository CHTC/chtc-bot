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
    db = boto3.resource(
        "dynamodb",
        region_name=os.environ["dynamo_region"],
        config=botocore.client.Config(),
    ).Table(os.environ["dynamo_table"])

    response = db.query(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": "lambda.py"},
    )
    if len(response["Items"]) == 0:
        return { "statusCode": 500, "body": json.dumps(f"database not configured"), }

    firstResponse = response["Items"][0]
    lastUpdateSeen = float(firstResponse["ts"])
    sharedSecret = firstResponse["ss"]

    d = feedparser.parse(
        "https://htcondor-wiki.cs.wisc.edu/index.cgi/timeline.rss?d=90"
    )
    lastUpdate = time.mktime(d.feed.updated_parsed)

    if lastUpdateSeen < lastUpdate:
        db.update_item(
            Key={"id": "lambda.py"},
            UpdateExpression="set ts = :ts",
            ExpressionAttributeValues={":ts": str(lastUpdate)},
            ReturnValues="UPDATED_NEW",
        )

        newEntries = []
        for entry in d.entries:
            published = time.mktime(entry.published_parsed)
            if lastUpdateSeen < published:
                newEntries.append(entry)

        requests.post(
            "https://chtc-bot.herokuapp.com/rss",
            headers={'Content-Type': 'application/json', 'X-Shared-Secret': sharedSecret},
            json=newEntries
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Feed updated at {lastUpdate}."),
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(f"No feed updates since {lastUpdate}."),
        }


if __name__ == "__main__":
    print(handler(None, None))
