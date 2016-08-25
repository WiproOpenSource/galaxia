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
from galaxia.gapi.handler.v1 import catalogue_handler
import logging


log = logging.getLogger(__name__)


class CatalogueController(object):
    @expose(generic=True)
    def index(self):
        unit_type = request.GET.get('unit_type')
        search_string = request.GET.get('search_string')
        search_type = request.GET.get('search_type')
        sub_type = request.GET.get('sub_type')
        handler = catalogue_handler.CatalogueHandler()
        log.info("Received request to get all %s", unit_type)
        unit_list = handler.get_units(unit_type, search_string, search_type, sub_type)
        return unit_list
