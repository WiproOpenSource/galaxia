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

from galaxia.common.prometheus import prometheus_helper
import logging
import json
from oslo_config import cfg

API_SERVICE_OPTS = [
    cfg.StrOpt('threshold_time',
               default='20',
               help='Threshold time'),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gapi', title='Options for the\
                                                    api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
CONF.set_override('threshold_time', CONF.gapi.threshold_time, opt_group)


log = logging.getLogger(__name__)


class StatusHandler(object):

    def get_units(self, unit_type, search_string, search_type, time_interval, status):
        if unit_type in self._function:
            return self._function[unit_type](search_string, search_type, time_interval, status, CONF.gapi.threshold_time)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def container(self, search_string, search_type, time_interval, status, threshold_time):
        list1 = ["Name", "Status"]
        i=0
        names_list, status_list = prometheus_helper.get_containers_by_status(search_string,
                                                                             search_type,
                                                                             time_interval,
                                                                             status,
                                                                             threshold_time)
        return json.dumps([{list1[i]: value for i, value in enumerate(x, i)} for x in zip(names_list, status_list)])