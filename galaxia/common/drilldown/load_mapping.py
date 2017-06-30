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

import yaml
from oslo_config import cfg

DRILLDOWN_OPTS = [
    cfg.StrOpt('mappingfile'
               ),
]

opt_group = cfg.OptGroup(name='drilldown', title='Options for the drilldown')
cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(DRILLDOWN_OPTS, opt_group)
#cfg.CONF.set_override('mappingfile', cfg.CONF.drilldown.mappingfile, opt_group)

odict = {}
datasource = ''

class MappingFile():

    def __init__(self, tlabel, slabel, rfields, nfields, dsource ):
        self.tlabel = tlabel
        self.slabel = slabel
        self.rfields = rfields
        self.nfields = nfields
        self.dsource = dsource

    def getTlabel(self):
        return self.tlabel

    def getSlabel(self):
        return self.slabel

    def getRfields(self):
        return self.rfields

    def getNfields(self):
        return self.nfields

    def getDatasource(self):
        return self.dsource

def initialize():
    f = cfg.CONF.drilldown.mappingfile
    with open(f, 'r') as stream:
        a = yaml.load_all(stream)
        for dictio in a:
            for key, value in dictio.iteritems():
                    for mylist in value:
                        obj = MappingFile(mylist['sourcelabel'], mylist['targetlabel'], mylist['returnfields'],
                                          mylist['nextfields'], mylist['datasource'])
                        odict[mylist['sourcelabel']] = obj

def getrelabelconfigs():
    rldict = {}
    for key, value in odict.iteritems():
        rldict[key] = MappingFile.getSlabel(value)
    return rldict