from pecan import expose
from pecan import request
from galaxia.gapi.handler.v1 import status_handler
import logging


log = logging.getLogger(__name__)


class StatusController(object):
    @expose(generic=True)
    def index(self):
        time_interval = request.GET.get('time_interval')
        unit_type = request.GET.get('unit_type')
        search_string = request.GET.get('search_string')
        search_type = request.GET.get('search_type')
        status = request.GET.get('status')
        handler = status_handler.StatusHandler()
        unit_list = handler.get_units(unit_type, search_string, search_type, time_interval, status)
        return unit_list
