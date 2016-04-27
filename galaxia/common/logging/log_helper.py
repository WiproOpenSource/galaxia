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

"""Helper to setup logging for all the modules"""

import logging


def setup_logging(file_location, log_level):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -\
                        %(message)s', filename=file_location, level=log_level)
