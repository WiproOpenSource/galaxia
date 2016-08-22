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


# Script to populate the metrics table
# Usage
# python create_supported_metrics.py --target http://192.168.76.20:9100/metrics
# --unit-type node --subtype node --dbhost localhost --username root --password root

from galaxia.common.prometheus import metrics_parser
from optparse import OptionParser
from sqlalchemy import create_engine
from galaxia.gdata.common import query_list

parser = OptionParser()
parser.add_option("--target", help="Scrape Target ")
parser.add_option("--unit-type", help="Type of metrics")
parser.add_option("--subtype", help="Subtype of metrics")
parser.add_option("--dbhost", help="IP address of Database host")
parser.add_option("--username", help="Username to login to database")
parser.add_option("--password", help="Password to login to database")
(options, args) = parser.parse_args()

db_url = "mysql"+"://"+options.username+":"+options.password+"@"+options.dbhost
galaxia_db_url = db_url + "/galaxia"
print "Connecting to "+"mysql" + " database@"+ options.dbhost
engine = create_engine(galaxia_db_url)
conn = engine.connect()

help_content = metrics_parser.main(options.target)
sql_query = query_list.INSERT_INTO_METRICS

for i in help_content:
    metric_type = i['type']
    metric_name = i['name']
    metric_help = i['help']
    params = [metric_name, options.unit_type, options.subtype, metric_help, metric_type ]
    conn.execute(sql_query, params)