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

from __future__ import unicode_literals
import sys
import json
from galaxia.gmiddleware.handler import client
try:
    import StringIO
except ImportError:
    # Python 3
    import io as StringIO

headers = {
        "Accept": "text/html",
        "Accept-Charset": "utf-8"
    }

class Metric(object):
    def __init__(self, name, documentation, typ):
        self.name = name
        self.documentation = documentation
        self.type = typ
        self.samples = []


def text_string_to_metric_families(text):
    for metric_family in text_fd_to_metric_families(StringIO.StringIO(text)):
      yield metric_family


def _unescape_help(text):
    result = []
    slash = False

    for char in text:
        if slash:
            if char == '\\':
                result.append('\\')
            elif char == 'n':
                result.append('\n')
            else:
                result.append('\\' + char)
            slash = False
        else:
          if char == '\\':
              slash = True
          else:
              result.append(char)

    if slash:
        result.append('\\')

    return ''.join(result)


def _parse_sample(text):
    name = []
    labelname = []
    labelvalue = []
    value = []
    labels = {}

    state = 'name'

    for char in text:
        if state == 'name':
            if char == '{':
                state = 'startoflabelname'
            elif char == ' ' or char == '\t':
                state = 'endofname'
            else:
                name.append(char)
        elif state == 'endofname':
            if char == ' ' or char == '\t':
                pass
            elif char == '{':
                state = 'startoflabelname'
            else:
                value.append(char)
                state = 'value'
        elif state == 'startoflabelname':
            if char == ' ' or char == '\t':
                pass
            elif char == '}':
                state = 'endoflabels'
            else:
                state = 'labelname'
                labelname.append(char)
        elif state == 'labelname':
            if char == '=':
                state = 'labelvaluequote'
            elif char == ' ' or char == '\t':
                state = 'labelvalueequals'
            elif char == '}':                        #Change to accomodate extra comma in metrics labels
                state = 'endoflabels'
            else:
                labelname.append(char)
        elif state == 'labelvalueequals':
            if char == '=':
                state = 'labelvaluequote'
            elif char == ' ' or char == '\t':
                pass
            else:
                raise ValueError("Invalid line: " + text)
        elif state == 'labelvaluequote':
            if char == '"':
                state = 'labelvalue'
            elif char == ' ' or char == '\t':
                pass
            else:
                raise ValueError("Invalid line: " + text)
        elif state == 'labelvalue':
            if char == '\\':
                state = 'labelvalueslash'
            elif char == '"':
                labels[''.join(labelname)] = ''.join(labelvalue)
                labelname = []
                labelvalue = []
                state = 'nextlabel'
            else:
                labelvalue.append(char)
        elif state == 'labelvalueslash':
            state = 'labelvalue'
            if char == '\\':
                labelvalue.append('\\')
            elif char == 'n':
                labelvalue.append('\n')
            elif char == '"':
                labelvalue.append('"')
            else:
                labelvalue.append('\\' + char)
        elif state == 'nextlabel':
            if char == ',':
                state = 'labelname'
            elif char == '}':
                state = 'endoflabels'
            elif char == ' ' or char == '\t':
                pass
            else:
                raise ValueError("Invalid line: " + text)
        elif state == 'endoflabels':
            if char == ' ' or char == '\t':
                pass
            else:
                value.append(char)
                state = 'value'
        elif state == 'value':
            if char == ' ' or char == '\t':
                # Timestamps are not supported, halt
                break
            else:
                value.append(char)
    name = ''.join(name)
    json_obj = {"label": labels}
    return json_obj

def text_fd_to_metric_families(fd):
    name = ''
    documentation = ''
    typ = 'untyped'
    samples = []
    allowed_names = []
    labels = []

    def build_metric(name, documentation, typ, samples):
        metric = Metric(name, documentation, typ)
        metric.samples = samples
        return metric

    for line in fd:
        line = line.strip()

        if line.startswith('#'):
            parts = line.split(None, 3)
            if len(parts) < 2:
                continue
            if parts[1] == 'HELP':
                if parts[2] != name:
                    if name != '':
                        yield build_metric(name, documentation, typ, samples)
                    # New metric
                    name = parts[2]
                    typ = 'untyped'
                    samples = []
                    allowed_names = [parts[2]]
                if len(parts) == 4:
                  documentation = _unescape_help(parts[3])
                else:
                  documentation = ''
            elif parts[1] == 'TYPE':
                if parts[2] != name:
                    if name != '':
                        yield build_metric(name, documentation, typ, samples)
                    # New metric
                    name = parts[2]
                    documentation = ''
                    samples = []
                typ = parts[3]
                allowed_names = {
                    'counter': [''],
                    'gauge': [''],
                    'summary': ['_count', '_sum', ''],
                    'histogram': ['_count', '_sum', '_bucket'],
                    }.get(typ, [parts[2]])
                allowed_names = [name + n for n in allowed_names]
            else:
                # Ignore other comment tokens
                pass
        elif line == '':
            # Ignore blank lines
            pass
        else:
            sample = _parse_sample(line)
            yield  build_metric(name, documentation, typ, sample)
            name = ''
            documentation = ''
            typ = 'untyped'

    if name != '':
        yield build_metric(name, documentation, typ, samples)


def main(target):
    list_of_jsons = []
    dict1 = {}
    dict2 = []
    i = 0
    resp = client.http_request("GET", target, headers, None, None, None)
    content = resp.iter_lines(decode_unicode=True)
    for lines in content:
        if "HELP" in lines:
            if bool(dict1):
                 #dict1.update({'labels': dict2})
                 list_of_jsons.append(dict1)
                 dict1={}
                 dict2=[]

        for family in text_string_to_metric_families(lines):
            if family.name is not '' and family.documentation is not '':
               help_json = {'name': family.name, 'help': family.documentation}
               dict1.update(help_json)
            elif family.name is not '' and family.type is not '':
               type_json = {'type': family.type}
               dict1.update(type_json)
            else:
                dict2.append(family.samples)
    if bool(dict1):
        #dict1.update({'labels': dict2})
        list_of_jsons.append(dict1)

    return list_of_jsons