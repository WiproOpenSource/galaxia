from pecan import expose
from pecan import request
from galaxia.gapi.handler.v1 import label_handler
import logging


log = logging.getLogger(__name__)


class LabelController(object):
    @expose(generic=True)
    def index(self):
        meter_name = request.GET.get('meter_name')
        handler = label_handler.LabelHandler()
        labels_list = handler.get_labels(meter_name)
        return labels_list
