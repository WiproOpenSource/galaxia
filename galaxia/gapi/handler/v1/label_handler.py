from galaxia.common.prometheus import prometheus_helper
import logging
import json
from oslo_config import cfg

log = logging.getLogger(__name__)


class LabelHandler(object):

    def get_labels(self, meter_name):
        labels_list = prometheus_helper.get_labels(meter_name)
        return json.dumps(labels_list)

