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

from galaxia.gapi.handler.v1 import register_handler

log = logging.getLogger(__name__)


class RegisterController(object):

    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

    # Method to register an agent, app or service discovery
    @index.when(method='POST', template='json')
    def post(self, **kwargs):
        log.info("Received request to onboard")

        handler = register_handler.RegisterHandler()
        resp = handler.register(**kwargs)
        return resp

    # Method to delete an agent, app or service discovery
    @index.when(method='DELETE', template='json')
    def index_delete(self, **kwargs):
        log.info("Received request to DeBoard")

        handler = register_handler.RegisterHandler()
      #  resp = handler.dregister(**kwargs)
       # return resp

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

