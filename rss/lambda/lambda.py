import os
import sys
import time
import json
import botocore, boto3

# This is stupid, but you can't explicitly import module dependencies.
sys.path.append("./libs")

import feedparser
import requests


def get_dynamo_db_table_from_environment():
    return boto3.resource(
        "dynamodb",
        region_name=os.environ["dynamo_region"],
        config=botocore.client.Config(),
    ).Table(os.environ["dynamo_table"])


def get_item_from_table(table, key):
    response = table.query(
        KeyConditionExpression="id = :id", ExpressionAttributeValues={":id": key},
    )
    if len(response["Items"]) == 0:
        return None
    else:
        return response["Items"][0]


def set_attribute_of_item(table, key, attribute, value):
    return table.update_item(
        Key={"id": key},
        UpdateExpression=f"set {attribute} = :attribute",
        ExpressionAttributeValues={":attribute": value},
        ReturnValues="UPDATED_NEW",
    )


def handler(event, context):
    table = get_dynamo_db_table_from_environment()
    state = get_item_from_table(table, "lambda.py")
    if state is None:
        return {
            "statusCode": 500,
            "body": json.dumps(f"database not configured"),
        }

    last_update_seen = float(state["last_update_seen"])
    rss_shared_secret = state["rss_shared_secret"]

    d = feedparser.parse(
        "https://htcondor-wiki.cs.wisc.edu/index.cgi/timeline.rss?d=90"
    )
    last_update = time.mktime(d.feed.updated_parsed)

    if last_update_seen < last_update:
        set_attribute_of_item(table, "lambda.py", "last_update_seen", str(last_update))
        newEntries = []
        for entry in d.entries:
            published = time.mktime(entry.published_parsed)
            if last_update_seen < published:
                newEntries.append(entry)

        requests.post(
            os.environ["bot_rss_api_endpoint"],
            headers={
                "Content-Type": "application/json",
                "X-Shared-Secret": rss_shared_secret,
            },
            json=newEntries,
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Feed updated at {last_update}."),
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(f"No feed updates since {last_update}."),
        }


if __name__ == "__main__":
    print(handler(None, None))
