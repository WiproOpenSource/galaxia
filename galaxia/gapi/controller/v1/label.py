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

from pecan import expose
from pecan import request
from galaxia.gapi.handler.v1 import label_handler
import logging


log = logging.getLogger(__name__)


class LabelController(object):
    @expose(generic=True)
    def index(self):
        meter_name = request.GET.get('meter_name')
        unit_type = request.GET.get('unit_type')
        search_type = request.GET.get('search_type')
        search_string = request.GET.get('search_string')
        handler = label_handler.LabelHandler()
        labels_list = handler.get_labels(meter_name, unit_type, search_type, search_string)
        return labels_list
