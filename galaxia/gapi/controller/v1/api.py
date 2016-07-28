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

"""v1 API Controller"""

import logging

from pecan import expose
from pecan import request
from webob.exc import status_map

from galaxia.gapi.handler.v1 import api as api_handler

log = logging.getLogger(__name__)


class DashboardController(object):

    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

    # Method to update a Dashboard
    @index.when(method='POST', template='json')
    def post(self, **kwargs):
        log.info("Received request to update a dashboard")

        handler = api_handler.ApiHandler()
        resp = handler.update_dashboard(**kwargs)
        return resp

    # Method to create a Dashboard
    @index.when(method='PUT', template='json')
    def index_put(self, **kwargs):
        log.info("Received request to create dashboard")

        handler = api_handler.ApiHandler()
        resp = handler.create(**kwargs)
        return resp

    # Method to delete a Dashboard
    @index.when(method='DELETE', template='json')
    def index_delete(self, **kwargs):
        log.info("Received request to Delete dashboard")

        handler = api_handler.ApiHandler()
        resp = handler.delete_dashboard(**kwargs)
        return resp

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)


class MetricsController(object):

    @expose(generic=True)
    def index(self):
        log.info("Received request to List Metrics")
        unit_type = request.GET.get('type')
        handler = api_handler.ApiHandler()
        resp = handler.get_metrics(unit_type)
        return resp

    @index.when(method='POST', template='json')
    def sample(self, **kwargs):
        log.info("Received request to get sample for meter ") #+meter_name)
        handler = api_handler.ApiHandler()
        resp = handler.get_sample(**kwargs)
        #resp = handler.get_sample(meter_name, search_string, search_type, type)
        return resp

class MetricsExporter(object):
    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

    # Method to create a Metrics Exporter
    @index.when(method='POST', template='json')
    def post(self, **kwargs):
        log.info("Received request to create a metrics exporter")

        handler = api_handler.ApiHandler()
        resp = handler.create_metrics_exporter(**kwargs)
        return resp
