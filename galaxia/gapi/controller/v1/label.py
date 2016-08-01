from pecan import expose
from pecan import request
from galaxia.gapi.handler.v1 import label_handler
import logging


log = logging.getLogger(__name__)


class LabelController(object):
    @expose(generic=True)
    def index(self):
        meter_name = request.GET.get('meter_name')
        unit_type = request.GET.get('unit_type')
        search_type = request.GET.get('search_type')
        search_string = request.GET.get('search_string')
        handler = label_handler.LabelHandler()
        labels_list = handler.get_labels(meter_name, unit_type, search_type, search_string)
        return labels_list
