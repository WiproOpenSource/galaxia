from galaxia.common.prometheus import prometheus_helper
import logging
import json
from oslo_config import cfg

API_SERVICE_OPTS = [
    cfg.StrOpt('threshold_time',
               default='20',
               help='Threshold time'),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gapi', title='Options for the\
                                                    api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
CONF.set_override('threshold_time', CONF.gapi.threshold_time, opt_group)


log = logging.getLogger(__name__)


class StatusHandler(object):

    def get_units(self, unit_type, search_string, search_type, time_interval, status):
        if unit_type in self._function:
            return self._function[unit_type](search_string, search_type, time_interval, status, CONF.gapi.threshold_time)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def container(self, search_string, search_type, time_interval, status, threshold_time):
        list1 = ["Name", "Status"]
        i=0
        names_list, status_list = prometheus_helper.get_containers_by_status(search_string,
                                                                             search_type,
                                                                             time_interval,
                                                                             status,
                                                                             threshold_time)
        return json.dumps([{list1[i]: value for i, value in enumerate(x, i)} for x in zip(names_list, status_list)])