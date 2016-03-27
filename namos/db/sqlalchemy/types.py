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


import json
import uuid

from sqlalchemy.dialects import mysql
from sqlalchemy.types import String
from sqlalchemy.types import Text
from sqlalchemy.types import TypeDecorator


class Json(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.LONGTEXT())
        else:
            return self.impl

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Uuid(TypeDecorator):
    impl = String(36)

    def process_bind_param(self, value, dialect):
        if value is not None:
            try:
                uuid.UUID(value, version=4)
            except ValueError:
                raise ValueError(
                    "Invalid format. It should be in UUID v4 format")

        return value

    def process_result_value(self, value, dialect):
        return value


class LongText(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.LONGTEXT())
        else:
            return self.impl
