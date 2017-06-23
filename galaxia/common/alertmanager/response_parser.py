import json

def get_alert_details(resp):
    result_list = json.loads(resp)['data']
    return result_list