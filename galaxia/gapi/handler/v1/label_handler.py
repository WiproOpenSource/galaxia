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

log = logging.getLogger(__name__)


class LabelHandler(object):

    def retrieve_labels(self, meter_name):
        labels_list = prometheus_helper.get_labels(meter_name)
        return labels_list

    def get_labels(self, meter_name, unit_type, search_type, search_string):
        #unit_type = kwargs['unit_type']
        if unit_type in self._function:
            return self._function[unit_type](meter_name, search_type, search_string)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def app(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

    def node(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

    def container(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

