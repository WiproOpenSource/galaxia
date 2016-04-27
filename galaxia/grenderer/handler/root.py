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

"""Root handler for renderer"""


from galaxia.grenderer.handler import promdash_handler
from galaxia.grenderer.handler.docker import prometheus_handler

aggregator_handlers = {
        'prometheus': prometheus_handler,
    }

renderer_handlers = {
        'promdash': promdash_handler,
    }


def handler(aggregator, renderer, message):

    renderer_handler = renderer_handlers[renderer]
    renderer_handler.draw_dashboard(message)


def delete_handler(aggregator, renderer, message):
    renderer_handler  = renderer_handlers[renderer]
    renderer_handler.delete_dashboard(message)
