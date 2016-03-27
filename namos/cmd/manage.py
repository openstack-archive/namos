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

import sys

from oslo_config import cfg
from oslo_utils import timeutils

from namos.common import config
from namos.common import exception
from namos.db import api
from namos.db import sample
from namos.db.sqlalchemy import migration


CONF = cfg.CONF
MANAGE_COMMAND_NAME = 'namos-manage'


class HeartBeat(object):
    def find_status(self, sw, report_interval=60):
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

    def report_status(self):
        # TODO(mrkanag) Make like Node: Service: worker: status
        for sw in api.service_worker_get_all(None):
            msg = '[%s] %s' % ('T' if self.find_status(sw) else 'F',
                               sw.name)
            print (msg)


class OsloConfigSchemaManager(object):
    def gen_schema(self):
        import json
        cfg_ns = dict()
        for cfg_ in api.config_schema_get_all(None):
            if cfg_.namespace not in cfg_ns:
                cfg_ns[cfg_.namespace] = dict()
            if cfg_.group_name not in cfg_ns[cfg_.namespace]:
                cfg_ns[cfg_.namespace][cfg_.group_name] = dict()
            cfg_ns[cfg_.namespace][cfg_.group_name][cfg_.name] = cfg_.to_dict()

        open(CONF.command.outputfile, 'w').write(json.dumps(cfg_ns))

    def sync(self):
        if CONF.command.gen:
            self.gen_schema()
            return

        sync_map = {}
        with open(CONF.command.syncfile) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                kv = line.split("=")
                sync_map[kv[0]] = kv[1].replace("\n", "")

        for k, v in sync_map.items():
            out_file = '%s/%s.json' % (CONF.command.outputdir or '/tmp', k)
            cmd = ('oslo-config-generator --config-file %s '
                   '--output-file %s --output-format json' %
                   (v, out_file))
            print ("\nSyncing %s " % cmd)
            import os
            os.system(cmd)

            if CONF.command.dbsync:
                import json
                conf_dict = json.loads(open(out_file).read())
                for grp, namespaces in conf_dict.items():
                    for namespace, opts in namespaces.items():
                        for name, opt in opts.items():
                            conf_ = dict(
                                namespace=namespace,
                                group_name=grp,
                                name=name,
                                default_value=opt['default'],
                                type=opt['type']['name'],
                                help=opt['help'],
                                required=opt['required'],
                                secret=opt['secret'],
                                mutable=opt['mutable']
                            )

                            try:
                                api.config_schema_create(None,
                                                         conf_)
                                _a = 'T'
                            except exception.AlreadyExist:
                                _a = 'F'

                            msg = '[%s] %s::%s::%s' % (_a,
                                                       namespace,
                                                       grp,
                                                       name)
                            print (msg)


class DBCommand(object):

    def upgrade(self):
        migration.upgrade(CONF.command.revision)

    def downgrade(self):
        migration.downgrade(CONF.command.revision)

    def revision(self):
        migration.revision(CONF.command.message, CONF.command.autogenerate)

    def stamp(self):
        migration.stamp(CONF.command.revision)

    def version(self):
        print(migration.version())

    def create_schema(self):
        migration.create_schema()

    def history(self):
        migration.history()

    def demo_data(self):
        if CONF.command.purge:
            sample.purge_demo_data()
        else:
            sample.populate_demo_data()


def add_command_parsers(subparsers):
    command_object = DBCommand()

    parser = subparsers.add_parser('upgrade')
    parser.set_defaults(func=command_object.upgrade)
    parser.add_argument('--revision', nargs='?')

    parser = subparsers.add_parser('downgrade')
    parser.set_defaults(func=command_object.downgrade)
    parser.add_argument('--revision', nargs='?')

    parser = subparsers.add_parser('stamp')
    parser.add_argument('--revision', nargs='?')
    parser.set_defaults(func=command_object.stamp)

    parser = subparsers.add_parser('revision')
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.set_defaults(func=command_object.revision)

    parser = subparsers.add_parser('version')
    parser.set_defaults(func=command_object.version)

    parser = subparsers.add_parser('history')
    parser.set_defaults(func=command_object.history)

    parser = subparsers.add_parser('create_schema')
    parser.set_defaults(func=command_object.create_schema)

    parser = subparsers.add_parser('demo_data')
    parser.add_argument('-p', '--purge', action='store_true')
    parser.set_defaults(func=command_object.demo_data)

    parser = subparsers.add_parser('oslo_config_schema')
    parser.add_argument('-f', '--syncfile')
    parser.add_argument('-o', '--outputdir')
    parser.add_argument('-j', '--outputfile')
    parser.add_argument('-s', '--dbsync', action='store_true')
    parser.add_argument('-g', '--gen', action='store_true')
    parser.set_defaults(func=OsloConfigSchemaManager().sync)

    parser = subparsers.add_parser('status')
    parser.set_defaults(func=HeartBeat().report_status)

command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help='Available commands',
                                handler=add_command_parsers)

CONF.register_cli_opt(command_opt)
# olso mandates to initialize the config after cli opt registration
config.init_conf(prog=MANAGE_COMMAND_NAME)


def main():
    try:
        CONF.command.func()
    except Exception as e:
        sys.exit("ERROR: %s" % e)


if __name__ == '__main__':
    main()
