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
Root handler for exporter
"""
import importlib

exporter_handlers = {
        'docker': "galaxia.gexporter.handler.docker.prometheus_ceilometer",
        'node': "galaxia.gexporter.handler.node.prometheus_ceilometer"
    }


def handler(source, target, message):
    if source == 'prometheus' and target == 'ceilometer':
            importlib.import_module(exporter_handlers[message['unit_type']]).schedule_job(message)



