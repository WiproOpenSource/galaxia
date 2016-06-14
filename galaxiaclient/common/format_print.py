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
format the command line print
"""

from tabulate import tabulate


def format_dict(dict1, header):
    """
    Prints the formatted output on command line

    :param dict1: dictionary object
    :param header: list of column names
    """
    if header=="keys":
        print tabulate(dict1, headers=header, tablefmt="fancy_grid", missingval="None")
    else:
        dict_list = []
        for key, value in dict1.iteritems():
            temp = [key, value]
            dict_list.append(temp)
        print tabulate(dict_list, headers=header, tablefmt="fancy_grid", missingval="None")
