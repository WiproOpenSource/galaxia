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

import logging

from pecan import expose

from galaxia.gapi.handler.v1 import alert_handler

log = logging.getLogger(__name__)


class AlertController(object):

    @expose(generic=True)
    def index(self):
        log.info("Received request to List Alerts")
        handler = alert_handler.AlertHandler()
        resp = handler.get_alerts()
        return resp

    @index.when(method='POST', template='json')
    def sample(self, **kwargs):
        log.info("Received request to create a custom alert")
        handler = alert_handler.AlertHandler()
        resp = handler.post_alert(**kwargs)
        return resp