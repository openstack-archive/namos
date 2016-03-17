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

from namos.db import api

REGION_LIST = [
    {'f7dcd175-27ef-46b5-997f-e6e572f320af':
         {'name': 'RegionOne',
          'keystone_region_id': 'region_one',
          'extra': {'location': 'bangalore'}}
    },
    {'f7dcd175-27ef-46b5-997f-e6e572f320b0':
         {'name': 'RegionTwo',
          'keystone_region_id': 'region_two',
          'extra': {'location': 'chennai'}}
    }
]

DEVICE_LIST = [
    # vCenter
    {'91007d3c-9c95-40c5-8f94-c7b071f9b577':
        {
            'name': 'Vmware_vCenter_1',
            'display_name': 'VMWare vCenter 1',
            'description': 'vCenter 5.0',
            'status': 'active',
            'extra': {'owner': 'mkr1481@namos.com'},
            'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
        },
    # Clusters
    {'d468ea2e-74f6-4a55-a7f4-a56d18e91c66':
         {
             'name': 'vmware_vc_Cluster_1',
             'display_name': 'VMWare vCenter 1 Cluster 1',
             'description': 'Cluster 1 having 3 hosts',
             'status': 'active',
             'extra': {'owner': 'mkr1481@namos.com',
                    'vcpus': 1000,
                    'ram_in_gb': 1024},
          'parent_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577',
          'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
    },
    {'6c97f476-8e27-4e21-8528-a5ec236306f3':
         {'name': 'vmware_vc_Cluster_2',
          'display_name': 'VMWare vCenter 1 Cluster 2',
          'description': 'Cluster 2 having 5 hosts',
          'status': 'active',
          'extra': {'owner': 'mkr1481@namos.com'},
          'parent_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577',
          'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
    },
    # Datastores
    {'fdab6c51-38fb-4fb1-a76f-9c243a8b8296':
         {'name': 'Vmware_vCenter_1_datastore_1',
          'display_name': 'VMWare vCenter 1 datastore 1',
          'description': 'vCenter 5.0 Datastore created from FC',
          'status': 'active',
          'extra': {'owner': 'mkr1481@namos.com',
                    'size_in_gb': '102400'},
          'parent_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577',
          'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
    },
    {'05b935b3-942c-439c-a6a4-9c3c73285430':
         {'name': 'Vmware_vCenter_1_datastore_2',
          'display_name': 'VMWare vCenter 1 datastore 2',
          'description': 'vCenter 5.0 Datastore created from FC',
          'status': 'active',
          'extra': {'owner': 'mkr1481@namos.com',
                    'size_in_gb': '10240'},
          'parent_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577',
          'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
    },
    # Switch
    {'f062556b-45c4-417d-80fa-4283b9c58da3':
         {'name': 'Vmware_vCenter_1_switch_1',
          'display_name': 'VMWare vCenter 1 Dist. vSwitch 1',
          'description': 'vCenter 5.0 distributed virtual switch',
          'status': 'active',
          'extra': {'owner': 'mkr1481@namos.com'},
          'parent_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577',
          'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'}
    }
]

ENDPOINT_LIST = [
    {'7403bf80-9376-4081-89ee-d2501661ca84':{
        'name': 'vcenter1_connection',
        'connection': {'host_ip': '10.1.1.3',
                       'host_port': 443,
                       'host_username': 'adminstrator',
                       'host_password': 'password'},
        'device_id': '91007d3c-9c95-40c5-8f94-c7b071f9b577'
    }}
]


DEVICE_DRIVER_CLASS_LIST = [
    {'0664e8c0-ff02-427e-8fa3-8788c017ad84': {
        'python_class': 'nova...vcdriver',
        'type': 'compute',
        'vendor': 'vmware-community'
    }},
    {'11caf99c-f820-4266-a461-5a15437a8144': {
        'python_class': 'cinder...vmdkdriver',
        'type': 'volume',
        'vendor': 'vmware-community'
    }},
    {'bb99ea96-fe6b-49e6-a761-faea92b79f75': {
        'python_class': 'neutron...nsxdriver',
        'type': 'network',
        'vendor': 'vmware-community'
    }}
]

DEVICE_DRIVER_LIST = [
    # nova
    {'3c089cdb-e1d5-4182-9a8e-cef9899fd7e5':{
        'endpoint_id': '7403bf80-9376-4081-89ee-d2501661ca84',
        'device_driver_class_id':'0664e8c0-ff02-427e-8fa3-8788c017ad84',
        'device_id': 'd468ea2e-74f6-4a55-a7f4-a56d18e91c66'
    }},
    # nova
    {'4e0360ae-0728-4bfd-a557-3ad867231787':{
        'endpoint_id': '7403bf80-9376-4081-89ee-d2501661ca84',
        'device_driver_class_id':'0664e8c0-ff02-427e-8fa3-8788c017ad84',
        'device_id': '6c97f476-8e27-4e21-8528-a5ec236306f3'
    }},
    # cinder
    {'92d5e2c1-511b-4837-a57d-5e6ee723060c':{
        'endpoint_id': '7403bf80-9376-4081-89ee-d2501661ca84',
        'device_driver_class_id':'11caf99c-f820-4266-a461-5a15437a8144',
        'device_id': 'fdab6c51-38fb-4fb1-a76f-9c243a8b8296'
    }},
    # cinder
    {'f3d807a0-eff0-4473-8ae5-594967136e05':{
        'endpoint_id': '7403bf80-9376-4081-89ee-d2501661ca84',
        'python_class_id':'11caf99c-f820-4266-a461-5a15437a8144',
        'device_id': '05b935b3-942c-439c-a6a4-9c3c73285430'
    }},
    # neutron
    {'f27eb548-929c-45e2-a2a7-dc123e2a1bc7':{
        'endpoint_id': '7403bf80-9376-4081-89ee-d2501661ca84',
        'python_class_id':'bb99ea96-fe6b-49e6-a761-faea92b79f75',
        'device_id': 'f062556b-45c4-417d-80fa-4283b9c58da3'
    }}
]


SERVICE_LIST =[
    {'11367a37-976f-468a-b8dd-77b28ee63cf4': {
        'name': 'nova_service',
        'keystone_service_id': 'b9c2549f-f685-4bc2-92e9-ba8af9c18599'
    }},
    {'809e04c1-2f3b-43af-9677-3428a0154216': {
        'name': 'cinder_service',
        'keystone_service_id': '9cc4c374-abb5-4bdc-9129-f0fa4bba0e0b'
    }},
    {'3495fa07-39d9-4d87-9f97-0a582a3e25c3': {
        'name': 'neutron_service',
        'keystone_service_id': 'b24e2884-75bc-4876-81d1-5b4fb6e92afc'
    }}
]

SERVICE_NODE_LIST = [
    {
        'a5073d58-2dbb-4146-b47c-4e5f7dc11fbe': {
            'name': 'd_network_node_1',
            'fqdn': 'network_node_1.devstack1.abc.com',
            'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'
        }
    },
    {
        '4e99a641-dbe9-416e-8c0a-78015dc55a2a': {
            'name': 'd_compute_node_1',
            'fqdn': 'compute_node_1.devstack.abc.com',
            'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'
        }
    },
    {
        'b92f4811-7970-421b-a611-d51c62972388': {
            'name': 'd_cloud-controller-1',
            'fqdn': 'cloud_controller_1.devstack1.abc.com',
            'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'
        }
    },
    {
        'e5913cd3-a416-40e1-889f-1a1b1c53001c': {
            'name': 'd_storage_node_1',
            'fqdn': 'storage_node_1.devstack.abc.com',
            'region_id': 'f7dcd175-27ef-46b5-997f-e6e572f320af'
        }
    }
]


SERVICE_COMPONENT_LIST = [
    # nova
    {
        '7259a9ff-2e6f-4e8d-b2fb-a529188825dd': {
            'name': 'd_nova-compute',
            'node_id': '4e99a641-dbe9-416e-8c0a-78015dc55a2a',
            'service_id': '11367a37-976f-468a-b8dd-77b28ee63cf4'
        }
    },
    {
        'e5e366ea-9029-4ba0-8bbc-f658e642aa54': {
            'name': 'd_nova-scheduler',
            'node_id': 'b92f4811-7970-421b-a611-d51c62972388',
            'service_id': '11367a37-976f-468a-b8dd-77b28ee63cf4'
        }
    },
    {
        'f7813622-85ee-4588-871d-42c3128fa14f': {
            'name': 'd_nova-api',
            'node_id': 'b92f4811-7970-421b-a611-d51c62972388',
            'service_id': '11367a37-976f-468a-b8dd-77b28ee63cf4'
        }
    },
    # cinder
    {
        'b0e9ac3f-5600-406c-95e4-f698b1eecfc6': {
            'name': 'd_cinder-volume',
            'node_id': 'e5913cd3-a416-40e1-889f-1a1b1c53001c',
            'service_id': '809e04c1-2f3b-43af-9677-3428a0154216'
        }
    },
    # neutron
    {
        '54f608bd-fb01-4614-9653-acbb803aeaf7':{
            'name': 'd_neutron-agent',
            'node_id': 'a5073d58-2dbb-4146-b47c-4e5f7dc11fbe',
            'service_id': '3495fa07-39d9-4d87-9f97-0a582a3e25c3'
        }
    }
]

SERVICE_WORKER_LIST = [
    # cluster-1
    {
        '65dbd695-fa92-4950-b8b4-d46aa0408f6a': {
            'name': 'd_nova-compute-esx-cluster1',
            'pid': '1233454343',
            'host': 'd_nova-compute-esx-cluster1',
            'service_component_id': '7259a9ff-2e6f-4e8d-b2fb-a529188825dd',
            'device_driver_id': '3c089cdb-e1d5-4182-9a8e-cef9899fd7e5'
        }
    },
    # cluster-2
    {
        '50d2c0c6-741d-4108-a3a2-2090eaa0be37': {
            'name': 'd_nova-compute-esx-cluster2',
            'pid': '1233454344',
            'host': 'd_nova-compute-esx-cluster2',
            'service_component_id': '7259a9ff-2e6f-4e8d-b2fb-a529188825dd',
            'device_driver_id': '4e0360ae-0728-4bfd-a557-3ad867231787'
        }
    },
    # datastore-1
    {
        '77e3ee16-fa2b-4e12-ad1c-226971d1a482': {
            'name': 'd_cinder-volume-vmdk-1',
            'pid': '09878654',
            'host': 'd_cinder-volume-vmdk-1',
            'service_component_id': 'b0e9ac3f-5600-406c-95e4-f698b1eecfc6',
            'device_driver_id': '92d5e2c1-511b-4837-a57d-5e6ee723060c'
        }
    },
    # datastore-2
    {
        '8633ce68-2b02-4efd-983c-49a460f6d7ef': {
            'name': 'd_cinder-volume-vmdk-2',
            'pid': '4353453',
            'host': 'd_cinder-volume-vmdk-2',
            'service_component_id': 'b0e9ac3f-5600-406c-95e4-f698b1eecfc6',
            'device_driver_id': 'f3d807a0-eff0-4473-8ae5-594967136e05'
        }
    },
    # vswitch
    {
        '5a3ac5b9-9186-45d8-928c-9e702368dfb4': {
            'name': 'd_neutron-agent',
            'pid': '2359234',
            'host': 'd_neutron-agent',
            'service_component_id': '54f608bd-fb01-4614-9653-acbb803aeaf7',
            'device_driver_id': 'f27eb548-929c-45e2-a2a7-dc123e2a1bc7'
        }
    },
]

CONFIG_LIST = [
    {
        'dc6aa02f-ba70-4410-a59c-5e113e629fe5': {
            'name':'vmware.host_ip',
            'value':'10.1.0.1',
            'help': 'VMWare vcenter IP address',
            'default':'',
            'type':'String',
            'required':True,
            'secret': False,
            'config_file':'/etc/nova/nova.conf',
            'service_worker_id': '65dbd695-fa92-4950-b8b4-d46aa0408f6a'
        }
    },
    {
        'dc6aa02f-ba70-4410-a59c-5e113e629f10': {
            'name':'vmware.host_username',
            'value':'Administraotr',
            'help': 'VMWare vcenter Username',
            'default':'Administrator',
            'type':'String',
            'required':True,
            'secret': False,
            'file':'/etc/nova/nova.conf',
            'service_worker_id': '65dbd695-fa92-4950-b8b4-d46aa0408f6a'
        }
    },
    {
        'dc6aa02f-ba70-4410-a59c-5e113e629f11': {
            'name':'vmware.host_password',
            'value':'password',
            'help': 'VMWare vcenter password',
            'default':'',
            'type':'String',
            'required':True,
            'secret': True,
            'file':'/etc/nova/nova.conf',
            'service_worker_id': '65dbd695-fa92-4950-b8b4-d46aa0408f6a'
        },
    }
]


def inject_id(value):
    if isinstance(value, dict):
        _id = value.keys()[0]
        value1 = value[_id].copy()
        value1['id'] = _id

        return value1
    return value


def _device_populate_demo_data():
    for region in REGION_LIST:
        region = inject_id(region)
        api.region_create(None, region)

    for device in DEVICE_LIST:
        device = inject_id(device)
        api.device_create(None, device)

    for device_endpoint in ENDPOINT_LIST:
        device_endpoint = inject_id(device_endpoint)
        api.device_endpoint_create(None, device_endpoint)

    # TODO(kanagaraj-manickam) Move this to alembic upgrade
    for device_driver_class in DEVICE_DRIVER_CLASS_LIST:
        device_driver_class = inject_id(device_driver_class)
        api.device_driver_class_create(None, device_driver_class)

    for device_driver in DEVICE_DRIVER_LIST:
        device_driver = inject_id(device_driver)
        api.device_driver_create(None, device_driver)


def _service_populate_demo_data():
    for service in SERVICE_LIST:
        service = inject_id(service)
        api.service_create(None, service)

    for service_node in SERVICE_NODE_LIST:
        service_node = inject_id(service_node)
        api.service_node_create(None, service_node)

    for service_component in SERVICE_COMPONENT_LIST:
        service_component = inject_id(service_component)
        api.service_component_create(None, service_component)

    for service_worker in SERVICE_WORKER_LIST:
        service_worker = inject_id(service_worker)
        api.service_worker_create(None, service_worker)

    for config in CONFIG_LIST:
        config = inject_id(config)
        api.config_create(None, config)


def populate_demo_data():
    _device_populate_demo_data()
    _service_populate_demo_data()


def _device_purge_demo_data():
    for device_driver in DEVICE_DRIVER_LIST:
        api.device_driver_delete(None, device_driver.keys()[0])

    for device_endpoint in ENDPOINT_LIST:
        api.device_endpoint_delete(None, device_endpoint.keys()[0])

    # Reverse the order of delete from child to parent device
    for device in DEVICE_LIST[::-1]:
        api.device_delete(None, device.keys()[0])

    # TODO(kanagaraj-manickam) Move this to alembic downgrade
    for device_driver_class in DEVICE_DRIVER_CLASS_LIST:
        api.device_driver_class_delete(None, device_driver_class.keys()[0])


def _service_purge_demo_data():
    for config in CONFIG_LIST:
        api.config_delete(None, config.keys()[0])
    for service_worker in SERVICE_WORKER_LIST:
        api.service_worker_delete(None, service_worker.keys()[0])

    for service_component in SERVICE_COMPONENT_LIST:
        api.service_component_delete(None, service_component.keys()[0])

    for service_node in SERVICE_NODE_LIST:
        api.service_node_delete(None, service_node.keys()[0])

    for service in SERVICE_LIST:
        api.service_delete(None, service.keys()[0])


def _region_purge_demo_data():
    for region in REGION_LIST:
        api.region_delete(None, region.keys()[0])


def purge_demo_data():
    _service_purge_demo_data()
    _device_purge_demo_data()
    _region_purge_demo_data()
