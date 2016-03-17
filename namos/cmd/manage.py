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

from namos.common import config
from namos.db import sample
from namos.db.sqlalchemy import migration


CONF = cfg.CONF
MANAGE_COMMAND_NAME = 'namos-manage'


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
