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

""" Client to make a http call """

import requests
from requests.auth import HTTPBasicAuth
import requests.exceptions as req_except
import logging

log = logging.getLogger(__name__)


def http_request(request_type, request_url, headers, payload, username,
                 password):
    """
    :param request_type - Valid values GET, POST, DELETE
    :param request_url - HTTP Request URL to galaxia api
    :param headers - HTTP Request headers
    :param payload - Payload for GET or POST request
    :param username -  UserName for Basic HTTP Auth
    :param password - Password for Basic HTTP Auth

    """
    resp = {}
    auth_object = None
    if username and password:
        auth_object = HTTPBasicAuth(username, password)

    try:
        if request_type == 'POST':
            resp = requests.post(request_url, data=payload, headers=headers,
                                 auth=auth_object)
        if request_type == 'GET':
            resp = requests.get(request_url, params=payload, headers=headers,
                                auth=auth_object)
        if request_type == 'PUT':
            resp = requests.put(request_url, data=payload, headers=headers,
                                auth=auth_object)

    except req_except.ConnectionError as ex:
        log.error("HTTP Client is unable to reach the service @ %s" % request_url)
        raise ex
    except req_except.HTTPError as ex:
        log.error("HTTP Client hit an unknown exception with error code %s and\
                  error %s" % ex.errno, ex.strerror)
        raise ex
    except Exception as ex:
        log.error(ex.errno)
        raise ex

    parse_http_response(resp, request_url)

    return resp


def concatenate_url(endpoint, url):
    """ concatenate endpoint & url
    :param endpoint: the base url for example http://localhost:port/v1
    :param url: the target url for example "/dashboard"
    :return: concatenated url for example http://localhost:port/v1/dashboard
    """
    return "%s/%s" % (endpoint.rstrip("/"), url.rstrip("/"))


def parse_response_for_container_names(resp):
    print "TBD"


def parse_http_response(resp, request_url):

    if resp.status_code == 200:
        pass
    elif resp.status_code == 404:
        log.error("Unable to reach the request resource @ %s" % request_url)

    elif resp.status_code == 401:
        log.error("Authentication failed for resource @ %s" % request_url)

    elif resp.status_code == 403:
        log.error("Authorization failed for resource @ %s with http error code\
                  %s" % (request_url, resp.status_code))

    elif resp.status_code == 408:
        log.error("Request timed out for resource @ %s with http error code %s"
                  % (request_url, resp.status_code))

    elif resp.status_code >= 500:
        log.error("Server failed to fullfil the request for resource @ %s with\
                  http error code %s" % (request_url, resp.status_code))
        raise Exception

    elif resp.status_code > 200:
        log.info("Request was accepted for processing for resource @ %s with\
                 http status code %s" % (request_url, resp.status_code))
    #    raise Exception

    else:
        log.error("Unable to process the request for resource @ %s with http\
                  error code %s" % (request_url, resp.status_code))
        raise Exception
