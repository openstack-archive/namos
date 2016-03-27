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

"""
SQLAlchemy models for namos database
"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
import uuid

from namos.db.sqlalchemy.types import Json
from namos.db.sqlalchemy.types import LongText
from namos.db.sqlalchemy.types import Uuid

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils


BASE = declarative_base()


class NamosBase(models.ModelBase,
                models.TimestampMixin):
    # TODO(kanagaraj-manickam) Make this as db independent
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = sqlalchemy.Column(Uuid, primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    name = sqlalchemy.Column(sqlalchemy.String(255),
                             unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    def expire(self, session, attrs=None):
        session.expire(self, attrs)

    def refresh(self, session, attrs=None):
        session.refresh(self, attrs)

    def delete(self, session):
        session.delete(self)
        session.flush()

    def update_and_save(self, values, session):
        self.update(values)
        self.save(session)

    def __str__(self):
        return "{id:%s, name:%s}" % (self.id, self.name)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        result = dict()
        for k, v in self.iteritems():
            if not str(k).endswith('_at'):
                result[k] = v
        return result


class SoftDelete(object):
    deleted_at = sqlalchemy.Column(sqlalchemy.DateTime)

    def soft_delete(self, session):
        self.update_and_save({'deleted_at': timeutils.utcnow()},
                             session=session)


class StateAware(object):
    status = sqlalchemy.Column(
        'status',
        sqlalchemy.String(64),
        nullable=False)


class Description(object):
    description = sqlalchemy.Column(sqlalchemy.Text)


class Extra(object):
    extra = sqlalchemy.Column(Json)


class Region(BASE,
             NamosBase,
             SoftDelete,
             Extra):
    __tablename__ = 'region'

    # Its of type String to match with keystone region id
    keystone_region_id = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False)


class Device(BASE,
             NamosBase,
             SoftDelete,
             StateAware,
             Description,
             Extra):
    __tablename__ = 'device'

    display_name = sqlalchemy.Column(sqlalchemy.String(255))
    parent_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('device.id'))
    region_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('region.id'),
        nullable=False)
    # TODO(kanagaraj-manickam) owner with keystone user id as one field??


class DeviceEndpoint(BASE,
                     NamosBase,
                     Extra):
    __tablename__ = 'device_endpoint'

    __table_args__ = (
        UniqueConstraint("device_id", "type"),
    )
    device_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('device.id'),
        nullable=False)
    type = sqlalchemy.Column(
        sqlalchemy.String(32)
    )
    connection = sqlalchemy.Column(
        Json,
        nullable=False)


class DeviceDriver(BASE,
                   NamosBase,
                   SoftDelete,
                   Extra):
    __tablename__ = 'device_driver'
    __table_args__ = (
        UniqueConstraint("device_id",
                         "endpoint_id",
                         "device_driver_class_id",
                         "service_worker_id"),
    )

    endpoint_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('device_endpoint.id')
    )

    device_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('device.id'))

    device_driver_class_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('device_driver_class.id')
    )
    service_worker_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_worker.id')
    )

# List of supported drivers in a given openstack release. so when
# openstack is released, migration script could be updated to pre-populate
# drivers in this table, which helps to track the drivers being released
# in the given openstack version.


class DeviceDriverClass(BASE,
                        NamosBase,
                        SoftDelete,
                        Extra):
    __tablename__ = 'device_driver_class'

    # TODO(kanagaraj-manickam) Correct the max python class path here
    python_class = sqlalchemy.Column(
        sqlalchemy.String(256),
        nullable=False,
        unique=True
    )
    # service type like compute, network, volume, etc
    type = sqlalchemy.Column(
        sqlalchemy.String(64),
        nullable=False
    )

    # TODO(kanagaraj-manickam) add vendor,
    # additional details like protocol, etc,
    # Capture all related driver details


class Service(BASE,
              NamosBase,
              SoftDelete,
              Extra):
    __tablename__ = 'service'

    keystone_service_id = sqlalchemy.Column(
        Uuid,
        nullable=False)


class ServiceNode(BASE,
                  NamosBase,
                  SoftDelete,
                  Description,
                  Extra):
    __tablename__ = 'service_node'

    fqdn = sqlalchemy.Column(
        sqlalchemy.String(128),
        nullable=False)
    region_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('region.id'))


class ServiceComponent(BASE,
                       NamosBase,
                       SoftDelete,
                       Description,
                       Extra):
    __tablename__ = 'service_component'

    __table_args__ = (
        UniqueConstraint("name", "node_id", "service_id"),
    )

    name = sqlalchemy.Column(sqlalchemy.String(255),
                             # unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    node_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_node.id'),
        nullable=False)
    service_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service.id'),
        nullable=False)


class ServiceWorker(BASE,
                    NamosBase,
                    SoftDelete,
                    Extra):
    __tablename__ = 'service_worker'

    __table_args__ = (
        UniqueConstraint("host", "service_component_id"),
    )

    name = sqlalchemy.Column(sqlalchemy.String(255),
                             # unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    pid = sqlalchemy.Column(
        sqlalchemy.String(64),
        nullable=False,
        unique=True
    )
    host = sqlalchemy.Column(
        sqlalchemy.String(248),
        nullable=False
    )
    service_component_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_component.id'),
        nullable=False)


class OsloConfigSchema(BASE,
                       NamosBase,
                       Extra):
    __tablename__ = 'oslo_config_schema'

    # TODO(mrkanag) Check whether conf is unique across all services or only
    # sepcific to namespace, otherwise uniqueconstraint is name, group_name
    __table_args__ = (
        UniqueConstraint("group_name", "name", "namespace"),
    )

    name = sqlalchemy.Column(sqlalchemy.String(255),
                             # unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    help = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
        default=''
    )
    type = sqlalchemy.Column(
        sqlalchemy.String(128),
        nullable=False
    )
    group_name = sqlalchemy.Column(
        sqlalchemy.String(128),
        nullable=False
    )
    namespace = sqlalchemy.Column(
        sqlalchemy.String(128),
        nullable=False
    )
    # TODO(mrkanag) default value is some time overriden by services, which
    # osloconfig allows, so this column should have values per given service
    default_value = sqlalchemy.Column(
        sqlalchemy.Text
    )
    required = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False
    )
    secret = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False
    )
    mutable = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False
    )


class OsloConfig(BASE,
                 NamosBase,
                 SoftDelete,
                 Extra):
    __tablename__ = 'oslo_config'

    __table_args__ = (
        UniqueConstraint("oslo_config_schema_id", "service_worker_id"),
    )

    name = sqlalchemy.Column(sqlalchemy.String(255),
                             # unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    value = sqlalchemy.Column(
        sqlalchemy.Text
    )
    oslo_config_file_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('oslo_config_file.id')
    )
    oslo_config_schema_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('oslo_config_schema.id'),
        nullable=False
    )
    service_worker_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_worker.id'),
        nullable=False
    )


class OsloConfigFile(BASE,
                     NamosBase,
                     SoftDelete,
                     Extra):
    __tablename__ = 'oslo_config_file'
    __table_args__ = (
        UniqueConstraint("name", "service_node_id"),
    )

    name = sqlalchemy.Column(sqlalchemy.String(255),
                             # unique=True,
                             nullable=False,
                             default=lambda: str(uuid.uuid4()))

    file = sqlalchemy.Column(
        LongText
    )
    # Always having last one updated the conf file
    service_component_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_component.id'),
        nullable=False
    )
    service_node_id = sqlalchemy.Column(
        Uuid,
        sqlalchemy.ForeignKey('service_node.id'),
        nullable=False
    )
