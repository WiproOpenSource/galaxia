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

""" RPC Handler for Metrics Exporter Service"""

from galaxia.gexporter.handler import root


class Controller(object):

    def export_metrics(self, ctxt, message):

        source_system = message['source_system']
        target_system = message['target_system']

        root.handler(source_system, target_system, message)
