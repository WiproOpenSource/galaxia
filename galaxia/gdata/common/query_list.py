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

""" List of SQL queries"""


INSERT_INTO_DASHBOARD = \
    "INSERT INTO DASHBOARD VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
IS_DASHBOARD_PRESENT = \
    "SELECT ID FROM dashboards WHERE NAME LIKE %s"
INSERT_INTO_DASHBOARDS = \
    "INSERT INTO dashboards VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
GET_OPENSTACK_TOKEN = \
    "SELECT TOKEN FROM OPENSTACK_TOKEN WHERE ID='one'"
UPDATE_TOKEN = \
    "UPDATE OPENSTACK_TOKEN SET TOKEN = %s WHERE ID='one'"
GET_METRICS = \
    "SELECT PROMETHEUS_NAME, DESCRIPTION FROM METRICS WHERE TYPE LIKE %s"
INSERT_INTO_EXPORTER = "INSERT INTO MEXPORTER VALUES (%s, %s)"
UPDATE_DASHBOARD = \
    "UPDATE DASHBOARD SET NAMES_LIST=%s, METRICS_LIST=%s, SEARCH_STRING=%s, SEARCH_TYPE=%s, DATE_UPDATED=%s WHERE NAME=%s"
DELETE_DASHBOARD = \
    "DELETE FROM DASHBOARD WHERE NAME=%s"
DELETE_FROM_DASHBOARDS= \
    "DELETE FROM dashboards WHERE NAME=%s"
LIST_DASHBOARD =\
     "SELECT NAME, NAMES_LIST, SEARCH_TYPE, SEARCH_STRING, METRICS_LIST , DASHBOARD_URL, EXCLUDE FROM DASHBOARD"
LIST_EXPORTER=\
     "SELECT EXPORTER_NAME, EXPORTER_ID FROM MEXPORTER"

