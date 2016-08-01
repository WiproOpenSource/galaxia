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

""" Create JSON for Promdash """

import json
import os
import logging

import galaxia.templates as template_data
from galaxia.common.prometheus import metrics_helper

log = logging.getLogger(__name__)
def create_json(name, unit_list, metrics_list, unit_type):
    """
    Creates json for promdash
    :param name: Name of the dashboard
    :param unit_list: Name list of the units
    :param metrics_list: List of metrics
    :return:
    """

    widgets_type = "graph"
    widgets_interpolation_method = "linear"
    widgets_resolution = 4

    show_legend = "always"

    axes_orientation = "left"
    axes_renderer = "line"
    axes_scale = "linear"
    axes_format = "kmbt"

    base_file = os.path.join(os.path.dirname(template_data.__file__),
                             "promdash.json")
    base_json = open(base_file).read()
    data = json.loads(base_json)

    data['name'] = name

    for i in unit_list:

        expressions_id = 0
        expressions_server_id = 1
        expressions_axis_id = 1
        axes_id = 1
        legend_id = 1

        expressions = []
        legendFormatStrings = []
        axes = []
        widget = {}
        widget["title"] = i
        widget["type"] = widgets_type
        widget["showLegend"] = show_legend
        widget["interpolationMethod"] = widgets_interpolation_method
        widget["resolution"] = widgets_resolution
        widget["endTime"] = None

        for j in json.loads(metrics_list):
            expression = {}
            legendFormatString = {}
            axe = {}

            if axes_id < 3:
                if axes_id > 1:
                    axe["orientation"] = "right"
                    axe['yMin'] = "1"
                    axe['yMax'] = "1000000000"
                    axe["scale"] = "log"
                else:
                    axe["orientation"] = axes_orientation
                axe["renderer"] = axes_renderer
                axe["scale"] = axes_scale
                axe["format"] = axes_format
                axe["id"] = axes_id
                axes.append(axe)

            expression["id"] = expressions_id
            expression["serverID"] = expressions_server_id

            if unit_type == 'docker':
                expression["expression"] = metrics_helper.get_metrics_with_labels(j, "name", i)
            elif unit_type == 'node':
                expression["expression"] = metrics_helper.get_metrics_with_labels(j, "instance", i)
            elif unit_type == 'jmx':
                expression["expression"] = metrics_helper.get_metrics_with_labels(j, "instance", i)

            expression["legendID"] = legend_id
            expression["axisID"] = 1
            legendFormatString["id"] = legend_id
            legendFormatString["name"] = j['name']

            axes_id += 1

            expressions.append(expression)
            legendFormatStrings.append(legendFormatString)

            expressions_id += 1
            expressions_axis_id += 1
            legend_id += 1

        widget["expressions"] = expressions
        widget["legendFormatStrings"] = legendFormatStrings
        widget["axes"] = axes
        data["dashboard_json"]["widgets"].append(widget)

    return json.dumps(data)
