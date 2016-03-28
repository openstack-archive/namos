# -*- coding: utf-8 -*-

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

from oslo_utils import timeutils


def find_status(sw, report_interval=60):
    status = False
    if sw.updated_at is not None:
        if ((timeutils.utcnow() - sw.updated_at).total_seconds()
                <= report_interval):
            status = True
    else:
        if ((timeutils.utcnow() - sw.created_at).total_seconds()
                <= report_interval):
            status = True

    return status
