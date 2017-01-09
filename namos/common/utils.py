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


def _to_list(list_in_str):
    '''string [a,b,c] -> python list [a, b ,c].'''
    def strip_out(s):
        start_idx = 0
        end_idx = len(s)
        if s[start_idx] == '[' \
                or s[start_idx] == '\'' \
                or s[start_idx] == '"':
            start_idx += 1
        if s[end_idx - 1] == ']' \
                or s[end_idx - 1] == '\'' \
                or s[end_idx - 1] == '"':
            end_idx -= 1
        return s[start_idx:end_idx]

    l = []
    for s in strip_out(list_in_str.strip()).split(','):
        s = str(strip_out(s.strip()))
        l.append(s)

    return l


def file_to_configs(file_path):
    with open(file_path, 'r') as file:
        section = ''
        conf_dict = dict()

        for line in file:
            if len(line.strip()) == 0:
                continue

            if line.strip().startswith('#'):
                continue

            if line.strip().startswith('['):
                section = line.replace('[', '').replace(']', '').strip()
                conf_dict[section] = dict()
                continue
            if section:
                kv = line.strip().split('=')
                # TODO(mrkanag) if values required, enable it here
                conf_dict[section][kv[0].strip()] = kv[1].strip().replace(
                    "\n", "")

    return conf_dict
