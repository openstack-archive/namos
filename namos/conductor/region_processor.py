# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_log import log

from namos.common import exception
from namos.db import api as db_api

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class RegionProcessor(object):
    def __init__(self,
                 context,
                 manager,
                 registration_info):
        self.registration_info = registration_info
        self.manager = manager
        self.context = context

    def process_region(self):
        # region
        # If region is not provided, make it as belongs to namos's region
        if not self.registration_info.get('region_name'):
            self.registration_info[
                'region_name'] = cfg.CONF.os_namos.region_name

        try:
            region = db_api.region_create(
                self.context,
                dict(name=self.registration_info.get('region_name'))
            )
            LOG.info('Region %s is created' % region)
        except exception.AlreadyExist:
            region = db_api.region_get_by_name(
                self.context,
                name=self.registration_info.get('region_name')
            )
            LOG.info('Region %s is existing' % region)

        return region.id
