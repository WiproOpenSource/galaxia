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


def get_metrics_with_labels(metrics_json, search_type, search_string):
    metrics_name = metrics_json['name']
    label_string = ''
    label_separator = ','
    i=0
    if 'label' in metrics_json and metrics_json['label'] is not None:
        for key,value in metrics_json['label'].iteritems():
            if i==1:
                label_string = label_string+label_separator
            label_string = label_string + key+'='+'"'+value+'"'
            i=1

    if search_type is not None and search_string is not None:
        if label_string is '':
            label_string = search_type+'=~'+ '"' + search_string + '"'
        else:
            label_string = label_string + label_separator + search_type+'=~'+ '"' + search_string + '"'

    return metrics_name+'{'+label_string+'}'
