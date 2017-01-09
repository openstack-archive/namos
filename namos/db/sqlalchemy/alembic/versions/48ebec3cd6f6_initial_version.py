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

"""Initial version

Revision ID: 48ebec3cd6f6
Revises: None
Create Date: 2014-10-31 10:57:41.695077

"""

# revision identifiers, used by Alembic.
revision = '48ebec3cd6f6'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'service',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('keystone_service_id', sa.Uuid(length=36), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'device_driver_class',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('python_class', sa.String(length=256), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=True),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'region',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('keystone_region_id', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'device',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('parent_id', sa.Uuid(length=36), nullable=True),
        sa.Column('region_id', sa.Uuid(length=36), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['device.id'], ),
        sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'service_node',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('fqdn', sa.String(length=128), nullable=False),
        sa.Column('region_id', sa.Uuid(length=36), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'device_endpoint',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('device_id', sa.Uuid(length=36), nullable=True),
        sa.Column('connection', sa.Json(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'service_component',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('node_id', sa.Uuid(length=36), nullable=False),
        sa.Column('service_id', sa.Uuid(length=36), nullable=False),
        sa.ForeignKeyConstraint(['node_id'], ['service_node.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'device_driver',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('endpoint_id', sa.Uuid(length=36), nullable=True),
        sa.Column('device_id', sa.Uuid(length=36), nullable=True),
        sa.Column('python_class_id', sa.Uuid(length=36), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
        sa.ForeignKeyConstraint(['endpoint_id'], ['device_endpoint.id'], ),
        sa.ForeignKeyConstraint(['python_class_id'],
                                ['device_driver_class.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )

    op.create_table(
        'service_worker',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('extra', sa.Json(), nullable=True),
        sa.Column('pid', sa.String(length=32), nullable=False),
        sa.Column('host', sa.String(length=248), nullable=False),
        sa.Column('service_component_id', sa.Uuid(length=36), nullable=False),
        sa.Column('device_driver_id', sa.Uuid(length=36), nullable=False),
        sa.ForeignKeyConstraint(['device_driver_id'], ['device_driver.id'], ),
        sa.ForeignKeyConstraint(['service_component_id'],
                                ['service_component.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
        )
# TODO(mrkanag) add oslo_config schema here


def downgrade():
    op.drop_table('oslo_config')
    op.drop_table('oslo_config_file_entry')
    op.drop_table('oslo_config_file')
    op.drop_table('oslo_config_schema')

    op.drop_table('os_capability')
    op.drop_table('os_capability_schema')

    op.drop_table('device_driver')
    op.drop_table('device_endpoint')
    op.drop_table('device_driver_class')
    op.drop_table('device')

    op.drop_table('service_worker')
    op.drop_table('service_component')
    op.drop_table('service_node')
    op.drop_table('service')

    op.drop_table('region')
