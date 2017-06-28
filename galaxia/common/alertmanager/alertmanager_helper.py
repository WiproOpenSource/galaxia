import os
import logging
import json
from galaxia.gmiddleware.handler import client
from galaxia.common.alertmanager import response_parser

log = logging.getLogger(__name__)

query_url = "alerts"

headers = {
        "Accept": "application/json"
    }

headers_post = {
        "Content-Type": "application/json"
    }


def create_payload(description, generator, labels):
    payload = []
    temp = {}
    annotation={"description": description, "generatorURL": generator}
    temp['annotations']=annotation
    temp['labels']=labels
    payload.append(temp)
    return json.dumps(payload)


def get_alerts():
    alertmanager_request_url = client.concatenate_url(
        os.getenv("alertmanager_endpoint"), query_url)
    resp = client.http_request("GET", alertmanager_request_url, headers, None,
                                   None, None)
    return json.dumps(response_parser.get_alert_details(resp.text))


def post_alert(description, generator, labels):
    alertmanager_request_url = client.concatenate_url(
        os.getenv("alertmanager_endpoint"), query_url)
    payload = create_payload(description, generator, labels)
    resp = client.http_request("POST", alertmanager_request_url, headers_post, payload,
                                   None, None)
    return resp.text
