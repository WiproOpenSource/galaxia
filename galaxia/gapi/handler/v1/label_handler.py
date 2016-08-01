from galaxia.common.prometheus import prometheus_helper
import logging
import json
from oslo_config import cfg

log = logging.getLogger(__name__)


class LabelHandler(object):

    def retrieve_labels(self, meter_name):
        labels_list = prometheus_helper.get_labels(meter_name)
        return json.dumps(labels_list)

    def get_labels(self, meter_name, unit_type, search_type, search_string):
        #unit_type = kwargs['unit_type']
        if unit_type in self._function:
            return self._function[unit_type](meter_name, search_type, search_string)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def app(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

    def node(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

    def container(self, meter_name, search_type, search_string):
        if search_type is not None and search_string is not None:
            meter = meter_name+"{"+ search_type +"="+'"'+search_string+'"'+"}"
        else:
            meter = meter_name
        return self.retrieve_labels(meter)

