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
Parse the action associated with galaxia command
"""
from galaxiaclient.common import client as cl

import os


class BaseParser(object):
    parser = None

    def __init__(self, parser):
        self.parser = parser

        self.parser.add_argument('action',
                                 default='help',
                                 help='Action to Perform')

        parsed, _ = self.parser.parse_known_args()
        action = vars(parsed).get('action')

        if action in self._actions:
            return self._actions[action]()
        else:
            print self.__doc__

    @property
    def _actions(self):
        """Action handler."""
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_')
                    and callable(getattr(self, attr)))
