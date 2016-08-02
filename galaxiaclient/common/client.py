# Copyright 2016 - Wipro Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Interface to create a http client and invoke request to galaxia api
"""

import json
import requests
import requests.exceptions as req_except


def create_request_data(**kwargs):
    """This method creates & returns json data
    :param kwargs: key/value pair
    :return: json data
    """

    data = {}
    for key, value in kwargs.iteritems():
        if "list" in key and not (value is None) and not "metrics_list" in key:
            temp = split_and_convert(key,value)
            data[key]=temp
        else:
            data[key]=value
    return json.dumps(data)


def split_and_convert(key, value):
    values = value.split(',')
    temp= []
    for i in values:
        temp.append(i)
    return temp


def http_request(request_type, request_url, headers, payload):
    """
    :param request_type - Valid values GET, POST, DELETE
    :param request_url - HTTP Request URL to galaxia api
    :param headers - HTTP Request headers
    :param payload - Payload for GET or POST request

    """

    resp = {}
    try:
        if request_type == 'POST':
            resp = requests.post(request_url, data = payload,
                                 headers = headers)

        if request_type == 'GET':
            resp = requests.get(request_url, params = payload,
                                headers = headers)

        if request_type == 'PUT':
            resp = requests.put(request_url, data = payload,headers = headers)

        if request_type == 'DELETE':
            resp = requests.delete(request_url, data = payload, headers=headers)


    except req_except.ConnectionError as ex:
        print "HTTP Client is unable to reach the service @ %s" % request_url
        print "Response Code is " + resp.status_code
        raise ex
    except req_except.HTTPError as ex:
        print "HTTP Client hit an unknown exception with error code %s\
              and error %s" % (ex.errno, ex.strerror)
    except Exception as ex:
        print "HTTP Client hit an exception with error %s" % ex.message
    parse_http_response(resp, request_url)

    return resp


def concatenate_url(endpoint, url):
    """ concatenate endpoint & url
    :param endpoint: the base url for example http://localhost:port/v1
    :param url: the target url for example "/dashboard"
    :return: concatenated url for example http://localhost:port/v1/dashboard
    """
    return "%s/%s" % (endpoint.rstrip("/"), url.rstrip("/"))


def parse_http_response(resp, request_url):

    if resp.status_code == 200:
        pass
    elif resp.status_code == 404:
        print "Unable to reach the request resource @ %s" % (request_url)
        raise Exception
    elif resp.status_code == 401:
        print "Authentication failed for resource @ %s" % request_url
        raise Exception
    elif resp.status_code == 403:
        print "Authorization failed for resource @ %s with http error code %s"\
              % (request_url, resp.status_code)
        raise Exception
    elif resp.status_code == 408:
        print "Request timed out for resource @ %s with http error code %s" \
              % (request_url, resp.status_code)
        raise Exception
    elif resp.status_code >= 500:
        print "Server failed to fullfil the request for resource @ %s with http\
              error code %s" % (request_url, resp.status_code)
        raise Exception
    else:
        print "Unable to process the request for resource @ %s with http error\
              code %s" % (request_url, resp.status_code)
        raise Exception
