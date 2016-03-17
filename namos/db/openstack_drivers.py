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


import urlparse

__all__ = ['get_drivers_config',
           'get_drivers_def']


def _get_db_name(*args, **kwargs):
    result = urlparse.urlparse(args[0])
    return '%s' % result.path.replace('/', '')


def _get_rpc_name(*args, **kwargs):
    return '%s' % args[0]


_DRIVERS_CONFIG = {
    # db
    'db_backend':{
        'sqlalchemy': { #driver_class
            # alias should be always end with driver class name.
            'alias':'database.backend:sqlalchemy',
        }
    },
    # TODO(mrkanag) sql_connectio is used in trove for db_backends
    # just check it
    'database.backend': {
        'sqlalchemy': { #driver_class
            'endpoint': {
                'name': 'database.connection',
                'connection': {
                    # mysql://root:password@127.0.0.1/neutron?charset=utf8
                    'database.connection': 'database.connection'
                }
            },
            'device': {
                'name': ['DB_%s', (_get_db_name, 'database.connection')]
            }
        }
    },
    # rpc
    'rpc_backend':{
        'rabbit': {
            'endpoint': {
                'name': 'rabbit_hosts',
                'connection': {
                    'rabbit_hosts': 'rabbit_hosts',
                    'rabbit_port': 'rabbit_port',
                    'rabbit_userid': 'rabbit_userid',
                    'rabbit_password': 'rabbit_password',
                    'control_exchange': 'control_exchange'
                }
            },
            'device': {
                'name': ['RPC_%s', (_get_rpc_name, 'control_exchange')]
            }
        },
        'nova.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        },
        'cinder.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        },
        'neutron.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        },
        'glance.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        },
        'heat.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        },
        'namos.openstack.common.rpc.impl_kombu': {
            'alias': 'rpc_backend:rabbit'
        }
    },
    # nova
    'compute_driver' : {
        'libvirt.LibvirtDriver': {
            'endpoint': {
                'type': 'libvirt.virt_type',
                'kvm': {
                    'name': 'host',
                    'connection': {
                        'libvirt.virt_type': 'libvirt.virt_type'
                    }
                },
                'qemu' : {
                    'name': 'host',
                    'connection': {
                        'libvirt.virt_type': 'libvirt.virt_type'
                    }
                },
                'xen': {
                    'name': 'xenapi_connection_url',
                    'connection': {
                        'xenapi_connection_url': 'xenapi_connection_url',
                        'xenapi_connection_username':
                            'xenapi_connection_username',
                        'xenapi_connection_password':
                            'xenapi_connection_password'
                    },
                    'device': {
                        'name': ['%s %s', 'libvirt.virt_type',
                                 'xenapi_connection_url']
                    }
                },
                'lxc': {
                    'name': 'host',
                    'connection': {
                        'libvirt.virt_type': 'libvirt.virt_type'
                    }
                },
            },
            'device': {
                'name': ['%s host %s', 'libvirt.virt_type', 'host']
            }
        },
        'vmwareapi.VMwareVCDriver':{
            'endpoint': {
                    'name': 'vmware.host_ip',
                    'connection': {
                        'vmware.host_ip': 'vmware.host_ip',
                        'vmware.host_username': 'vmware.host_username',
                        'vmware.host_password': 'vmware.host_password',
                        'vmware.cluster_name': 'vmware.cluster_name',
                        'vmware.datastore_regex': 'vmware.datastore_regex'
                    },
                    # When one driver supports mutiple devices, parent-child
                    # relation will be formed and parent usually has the
                    # endpoint associated with it, which is used by children
                    # devices
                    'child_device': {
                        # TODO(mrkanag) key should be comma separated or list,
                        # just check !!
                        'key': 'vmware.cluster_name',
                        'base_name': ['VMWare Cluster %s', 'vmware.host_ip']
                    # This name will be postfixed with device name got from key
                    }
            },
            'device': {
                'name': 'vmware.host_ip'
            }
        },
        'nova.virt.hyperv.driver.HyperVDriver': {
            'endpoint': {
                'name': 'host',
                'connection': {
                    'libvirt.type': 'libvirt.type'
                }
            },
            'device':{
                'name': ['Hyper-V host %s', 'host']
            }
        }
    },
    # cinder
    'volume_driver': {
        'cinder.volume.drivers.lvm.LVMISCSIDriver': {
            'endpoint': {
                'name': 'volume_group',
                'connection': {
                    'volume_group': 'volume_group',
                    'lvm_mirrors': 'lvm_mirrors',
                    'lvm_type': 'lvm_type'
                }
            },
            'device': {
                'name': ['%s@%s', 'volume_group', 'host']
            }
        },
        'cinder.volume.drivers.lvm.LVMISERDriver': {
            'alias': 'volume_driver:cinder.volume.drivers.lvm.LVMISCSIDriver'
        },
        'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver': {
            'endpoint': {
                'name': 'hp3par_api_url',
                'connection': {
                    'hp3par_api_url': 'hp3par_api_url',
                    'hp3par_username': 'hp3par_username',
                    'hp3par_password' : 'hp3par_password',
                    'hp3par_cpg': 'hp3par_cpg',
                    'san_ip': 'san_ip',
                    'san_login':'san_login',
                    'san_password': 'san_password',
                    'hp3par_iscsi_ips': 'hp3par_iscsi_ips',
                    'iscsi_ip_address': 'iscsi_ip_address'
                },
                'device': {
                    'name': ['%s@%s', 'hp3par_cpg', 'san_ip']
                }
            }
        },
        'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARFCDriver': {
            'alias': 'volume_driver:cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver'
        },
        'cinder.volume.drivers.san.hp.hp_lefthand_iscsi.HPLeftHandISCSIDriver':
        {
            'endpoint': {
                # TODO(mrkanag) type is not config param. what to do?
                'type': '#REST',
                '#CLIQ': {
                    'name': 'san_ip',
                    'connection': {
                        'san_ip': 'san_ip',
                        'san_login': 'san_login',
                        'san_password': 'san_password',
                        'san_ssh_port': 'san_ssh_port',
                        'san_clustername': 'san_clustername'
                    },
                    'device': {
                        'name': ['%s@%s', 'san_clustername', 'san_ip']
                    }
                },
                '#REST': {
                    'name': 'hplefthand_api_url',
                    'connection': {
                        'hplefthand_api_url': 'hplefthand_api_url',
                        'hplefthand_username': 'hplefthand_username',
                        'hplefthand_password': 'hplefthand_password',
                        'hplefthand_clustername': 'hplefthand_clustername'
                    },
                    'device': {
                        'name': ['%s@%s', 'hplefthand_clustername',
                                 'hplefthand_api_url']
                    }
                }
            }
        },
        'cinder.volume.drivers.coraid.CoraidDriver': {
            'endpoint': {
                'name': 'coraid_esm_address',
                'connection': {
                    'coraid_esm_address': 'coraid_esm_address',
                    'coraid_user': 'coraid_user',
                    'coraid_group': 'coraid_group',
                    'coraid_password': 'coraid_password',
                    'coraid_repository_key': 'coraid_repository_key'
                }
            },
            'device': {
                'name': ['coraid %s', 'coraid_esm_address']
            }
        },
        'cinder.volume.drivers.eqlx.DellEQLSanISCSIDriver': {
            'endpoint': {
                'name': 'san_ip',
                'connection': {
                    'san_ip': 'san_ip',
                    'san_login': 'san_login',
                    'san_password': 'san_password',
                    'eqlx_group_name': 'eqlx_group_name',
                    'eqlx_pool': 'eqlx_pool'
                }
            },
            'device': {
                'name': ['%s@%s', 'eqlx_group_name', 'san_ip']
            }
        },
        'cinder.volume.drivers.emc.emc_vmax_iscsi.EMCVMAXISCSIDriver': {
            'endpoint': {
                'name': 'iscsi_ip_address',
                'connection': {
                    'iscsi_ip_address': 'iscsi_ip_address',
                    # TODO(mrkanag) not sure what to do with config file
                    'cinder_emc_config_file': 'cinder_emc_config_file'
                }
            },
            'device': {
                'name': ['EMCVMAX %s', 'iscsi_ip_address']
            }
        },
        'cinder.volume.drivers.emc.emc_vmax_fc.EMCVMAXFCDriver': {
            'endpoint': {
                'name': '',
                'connection': {
                    'cinder_emc_config_file': 'cinder_emc_config_file'
                }
            },
            'device': {
                # TODO(mrkanag) fill it
                'name': ''
            }
        },
        'cinder.volume.drivers.emc.emc_cli_iscsi.EMCCLIISCSIDriver': {
            'endpoint': {
                'name': 'iscsi_ip_address',
                'connection': {
                    'iscsi_ip_address': 'iscsi_ip_address',
                    'san_ip': 'iscsi_ip_address',
                    'san_login': 'san_login',
                    'san_password': 'san_password',
                    'naviseccli_path': 'naviseccli_path',
                    'storage_vnx_pool_name': 'storage_vnx_pool_name',
                    'default_timeout': 'default_timeout',
                    'max_luns_per_storage_group': 'max_luns_per_storage_group'
                }
            },
            'device': {
                'name': ['EMC %s@%s', 'storage_vnx_pool_name', 'san_ip']
            }
        },
        'cinder.volume.drivers.glusterfs.GlusterfsDriver': {
            'endpoint': {
                'name': 'glusterfs_mount_point_base',
                'connection': {
                    'glusterfs_mount_point_base': 'glusterfs_mount_point_base',
                    'glusterfs_shares_config': 'glusterfs_shares_config'
                }
            },
            'device': {
                'name': ['Gfs %s', 'glusterfs_mount_point_base']
            }
        },
        'cinder.volume.drivers.hds.iscsi.HDSISCSIDriver': {
            'endpoint': {
                'name': 'HDS',
                'connection': {
                    'hds_hnas_iscsi_config_file': 'hds_hnas_iscsi_config_file'
                }
            },
            'device': {
                'name': 'HDS'
            }
        },
        'cinder.volume.drivers.hds.nfs.HDSNFSDriver': {
            'endpoint': {
                'name': '',
                'connection': {
                    'hds_hnas_nfs_config_file': 'hds_hnas_nfs_config_file'
                }
            },
            'device': {
                'name': 'HDS'
            }
        },
        'cinder.volume.drivers.hds.hds.HUSDriver': {
            'endpoint': {
                'name': '',
                'connection': {
                    'hds_cinder_config_file': 'hds_cinder_config_file'
                }
            },
            'device': {
                'name': 'HUS'
            }
        },
        'cinder.volume.drivers.hitachi.hbsd_fc.HBSDFCDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.hitachi.hbsd_iscsi.HBSDISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.san.hp.hp_msa_fc.HPMSAFCDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.huawei.HuaweiVolumeDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.ibm.gpfs.GPFSDriver': {
            'endpoint': {
                'name': '',
                'connection': {
                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.ibm.storwize_svc.StorwizeSVCDriver': {
            'endpoint': {
                'name': '',
                'connection': {
                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.xiv_ds8k.XIVDS8KDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.netapp.common.NetAppDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.netapp.iscsi.NetAppDirectCmodeISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.netapp.nfs.NetAppDirectCmodeNfsDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.netapp.iscsi.NetAppDirect7modeISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.netapp.nfs.NetAppDirect7modeNfsDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.nexenta.iscsi.NexentaISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.nexenta.nfs.NexentaNfsDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.nfs.NfsDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.prophetstor.dpl_fc.DPLFCDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.prophetstor.dpl_iscsi.DPLISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.pure.PureISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.sheepdog.SheepdogDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.solidfire.SolidFireDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.vmware.vmdk.VMwareVcVmdkDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.windows.WindowsDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.xenapi.sm.XenAPINFSDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.zadara.ZadaraVPSAISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.volume.drivers.zfssa.zfssaiscsi.ZFSSAISCSIDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        }
    },
    'backup_driver': {
        'cinder.backup.drivers.ceph': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.backup.drivers.swift': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.backup.drivers.tsm': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        }
    },
    'zone_driver': {
        'cinder.zonemanager.drivers.brocade.brcd_fc_zone_driver.BrcdFCZoneDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        },
        'cinder.zonemanager.drivers.cisco.cisco_fc_zone_driver.CiscoFCZoneDriver': {
            'endpoint': {
                'name': '',
                'connection': {

                }
            },
            'device': {
                'name': ''
            }
        }
    },
    # neutron
    # 'core_plugin': {
    #     'neutron.plugins.ml2.plugin.Ml2Plugin': {
    #
    #     }
    # },
    # 'service_plugins': {
    #     'neutron.services.l3_router.l3_router_plugin.L3RouterPlugin': {
    #
    #     }
    # },
    # 'service_providers.service_provider': {
    #
    # },
    'dhcp_driver': {
        'neutron.agent.linux.dhcp.Dnsmasq': {
            'endpoint': {
                'name': 'dhcp_domain',
                'connection': {
                    'dhcp_domain': 'dhcp_domain'
                }
            },
            'device': {
                'name': ['DHCP  %s', 'dhcp_domain']
            }
        }
    },
    'interface_driver': {
        'neutron.agent.linux.interface.OVSInterfaceDriver': {
             'endpoint': {
                'name': 'ovs_integration_bridge',
                'connection': {
                    'ovs_integration_bridge': 'ovs_integration_bridge'
                }
            },
            'device': {
                'name': ['OVS bridge %s', 'ovs_integration_bridge']
            }
        }
    },
    # 'extension_drivers': {
    #
    # },
    'ml2.mechanism_drivers': {
        'linuxbridge' : {
            'alias': 'ml2.mechanism_drivers:neutron.plugins.ml2.drivers.mech_linuxbridge.LinuxbridgeMechanismDriver'
        },
        'neutron.plugins.ml2.drivers.mech_linuxbridge.LinuxbridgeMechanismDriver': {
            'endpoint': {
                'name': '#Linux Bride',
                'connection': {
                }
            },
            'device': {
                'name': '#Linux Bride'
            }
        },
        'openvswitch': {
            'alias': 'ml2.mechanism_drivers:neutron.plugins.ml2.drivers.mech_openvswitch.OpenvswitchMechanismDriver'
        },
        'neutron.plugins.ml2.drivers.mech_openvswitch.OpenvswitchMechanismDriver': {
            'endpoint': {
                'name': '#OVS',
                'connection': {
                }
            },
            'device': {
                'name': '#OVS'
            }
        }
    },
    'ml2.type_drivers': {
        'local': {
            'alias': 'ml2.type_drivers:neutron.plugins.ml2.drivers.type_local.LocalTypeDriver'
        },
        'neutron.plugins.ml2.drivers.type_local.LocalTypeDriver': {
            'endpoint': {
                'name': '#Local Type',
                'connection': {
                }
            },
            'device': {
                'name': '#Local Type'
            }
        },
        'flat': {
            'alias': 'ml2.type_drivers:neutron.plugins.ml2.drivers.type_flat.FlatTypeDriver'
        },
        'neutron.plugins.ml2.drivers.type_flat.FlatTypeDriver': {
            'endpoint': {
                'name': '#FLAT Type',
                'connection': {
                }
            },
            'device': {
                'name': '#FLAT type'
            }
        },
        'vlan': {
            'alias': 'ml2.type_drivers:neutron.plugins.ml2.drivers.type_vlan.VlanTypeDriver'
        },
        'neutron.plugins.ml2.drivers.type_vlan.VlanTypeDriver': {
            'endpoint': {
                'name': '#VLAN Type',
                'connection': {
                }
            },
            'device': {
                'name': '#VLAN Type'
            }
        },
        'gre': {
            'alias': 'ml2.type_drivers:neutron.plugins.ml2.drivers.type_gre.GreTypeDriver'
        },
        'neutron.plugins.ml2.drivers.type_gre.GreTypeDriver': {
            'endpoint': {
                'name': '#GRE Type',
                'connection': {
                }
            },
            'device': {
                'name': '#GRE Type'
            }
        },
        'vxlan': {
            'alias': 'ml2.type_drivers:neutron.plugins.ml2.drivers.type_vxlan.VxlanTypeDriver'
        },
        'neutron.plugins.ml2.drivers.type_vxlan.VxlanTypeDriver': {
            'endpoint': {
                'name': '#VxLAN Type',
                'connection': {
                }
            },
            'device': {
                'name': '#VxLAN Type'
            }
        },
    },
    'firewall_driver': {
        'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver': {
            'endpoint': {
                'name': '#Firewall',
                'connection': {
                }
            },
            'device': {
                'name': '#Firewall'
            }
        },
        'nova.virt.firewall.NoopFirewallDriver' : {
            'endpoint': {
                'name': '#NoopFirewall',
                'connection': {
                }
            },
            'device': {
                'name': '#Firewall'
            }
        }
    },
    'SECURITY_GROUP.firewall_driver': {
        'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver': {
            'alias': 'firewall_driver:neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver'
        }
    },

    # 'dhcp_agent_manager': {
    #
    # },
    # 'l3_agent_manager': {
    #
    # },
    # Glance
    'glance_store.stores': {
        'file': {
            'alias': 'glance_store.stores:glance_store._drivers.filesystem.Store'
        },
        'filesystem': {
            'alias': 'glance_store.stores:glance_store._drivers.filesystem.Store'
        },
        'glance_store._drivers.filesystem.Store': {
            'endpoint': {
                'name': 'glance_store.filesystem_store_datadir',
                'connection': {
                    'glance_store.filesystem_store_datadir': 'glance_store.filesystem_store_datadir',
                    'glance_store.filesystem_store_datadirs': 'glance_store.filesystem_store_datadirs',
                    'glance_store.filesystem_store_file_perm': 'glance_store.filesystem_store_file_perm',
                    'glance_store.filesystem_store_metadata_file':
                        'glance_store.filesystem_store_metadata_file'
                }
            },
            'device': {
                'name': ['File System Store %s', 'glance_store.filesystem_store_datadir']
            }
        },
        'http': {
            'alias': 'glance_store.stores:glance_store._drivers.http.Store'
        },
        'https': {
            'alias': 'glance_store.stores:glance_store._drivers.http.Store'
        },
        'glance_store._drivers.http.Store': {
            'endpoint': {
                'name': '#http',
                'connection': {
                }
            },
            'device': {
                'name': '#http Image beackend'
            }
        },
        'cinder': {
            'alias': 'glance_store.stores:glance_store._drivers.cinder.Store'
        },
        'glance_store._drivers.cinder.Store': {
            'endpoint': {
                'name': '#Cinder Image Backend',
                'connection': {
                    'glance_store.cinder_endpoint_template': 'glance_store.cinder_endpoint_template',
                    'glance_store.cinder_api_insecure': 'glance_store.cinder_api_insecure',
                    'glance_store.cinder_ca_certificates_file':
                        'glance_store.cinder_ca_certificates_file',
                    'glance_store.cinder_catalog_info': 'glance_store.cinder_catalog_info',
                    'glance_store.cinder_http_retries': 'glance_store.cinder_http_retries'
                }
            },
            'device': {
                'name': '#Cinder Image Backend'
            }
         },
        'swift': {
            'alias': 'glance_store.stores:glance_store._drivers.swift.Store'
        },
        'glance_store._drivers.swift.Store': {
            'endpoint': {
                'name': 'glance_store.default_swift_reference',
                'connection': {
                    'glance_store.default_swift_reference': 'glance_store.default_swift_reference',
                    'glance_store.swift_enable_snet': 'glance_store.swift_enable_snet',
                    'glance_store.swift_store_admin_tenants': 'glance_store.swift_store_admin_tenants',
                    'glance_store.swift_store_auth_address': 'glance_store.swift_store_auth_address',
                    'glance_store.swift_store_auth_insecure': 'glance_store.swift_store_auth_insecure',
                    'glance_store.swift_store_auth_version': 'glance_store.swift_store_auth_version',
                    'glance_store.swift_store_config_file': 'glance_store.swift_store_config_file',
                    'glance_store.swift_store_container': 'glance_store.swift_store_container',
                    'glance_store.swift_store_create_container_on_put': 'glance_store.swift_store_create_container_on_put',
                    'glance_store.swift_store_endpoint_type': 'glance_store.swift_store_endpoint_type',
                    'glance_store.swift_store_key': 'glance_store.swift_store_key',
                    'glance_store.swift_store_large_object_chunk_size': 'glance_store.swift_store_large_object_chunk_size',
                    'glance_store.swift_store_large_object_size': 'glance_store.swift_store_large_object_size',
                    'glance_store.swift_store_multi_tenant': 'glance_store.swift_store_multi_tenant',
                    'glance_store.swift_store_region': 'glance_store.swift_store_region',
                    'glance_store.swift_store_retry_get_count': 'glance_store.swift_store_retry_get_count',
                    'glance_store.swift_store_service_type': 'glance_store.swift_store_service_type',
                    'glance_store.swift_store_ssl_compression': 'glance_store.swift_store_ssl_compression',
                    'glance_store.swift_store_user': 'glance_store.swift_store_user'
                }
            },
            'device': {
                'name': ['Swift Image backend %s', 'glance_store.default_swift_reference']
            }
        },
        'rbd': {
            'alias': 'glance_store.stores:glance_store._drivers.rbd.Store'
        },
        'glance_store._drivers.rbd.Store': {
            'endpoint': {
                'name': 'glance_store.rbd_store_pool',
                'connection': {
                    'glance_store.rbd_store_ceph_conf': 'glance_store.rbd_store_ceph_conf',
                    'glance_store.rbd_store_chunk_size': 'glance_store.rbd_store_chunk_size',
                    'glance_store.rbd_store_pool': 'glance_store.rbd_store_pool',
                    'glance_store.rbd_store_user': 'glance_store.rbd_store_user'
                }
            },
            'device': {
                'name': ['RBD Image backend %s', 'glance_store.rbd_store_pool']
            }
        },
        'sheepdog': {
            'alias': 'glance_store.stores:glance_store._drivers.sheepdog.Store'
        },
        'glance_store._drivers.sheepdog.Store': {
            'endpoint': {
                'name': 'glance_store.sheepdog_store_address',
                'connection': {
                    'glance_store.sheepdog_store_address': 'glance_store.sheepdog_store_address',
                    'glance_store.sheepdog_store_chunk_size': 'glance_store.sheepdog_store_chunk_size',
                    'glance_store.sheepdog_store_port': 'glance_store.sheepdog_store_port'
                }
            },
            'device': {
                'name': ['Sheepdog Image backend %s', 'glance_store.sheepdog_store_address']
            }
        },
        'gridfs': {
            'alias': 'glance_store.stores:glance_store._drivers.gridfs.Store'
        },
        'glance_store._drivers.gridfs.Store': {
            'endpoint': {
                'name': 'glance_store.mongodb_store_uri',
                'connection': {
                    'glance_store.mongodb_store_db': 'glance_store.mongodb_store_db',
                    'glance_store.mongodb_store_uri': 'glance_store.mongodb_store_uri'
                }
            },
            'device': {
                'name': ['Gird FS Image backend %s', 'glance_store.mongodb_store_db']
            }
        },
        's3': {
            'alias': 'glance_store.stores:glance_store._drivers.s3.Store'
        },
        's3+http': {
            'alias': 'glance_store.stores:glance_store._drivers.s3.Store'
        },
        's3': {
            'alias': 'glance_store.stores:glance_store._drivers.s3.Store'
        },
        'glance_store._drivers.s3.Store': {
            'endpoint': {
                'name': ['%s/%s', 'glance_store.s3_store_host', 'glance_store.s3_store_bucket'],
                'connection': {
                    'glance_store.s3_store_host': 'glance_store.s3_store_host',
                    'glance_store.s3_store_bucket': 'glance_store.s3_store_bucket',
                    'glance_store.s3_store_object_buffer_dir': 'glance_store.s3_store_object_buffer_dir',
                    'glance_store.s3_store_secret_key': 'glance_store.s3_store_secret_key',
                    'glance_store.s3_store_create_bucket_on_put': 'glance_store.s3_store_create_bucket_on_put',
                    'glance_store.s3_store_bucket_url_format': 'glance_store.s3_store_bucket_url_format',
                    'glance_store.s3_store_access_key': 'glance_store.s3_store_access_key'
                }
            },
            'device': {
                'name': ['S3 Image Backend %s/%s',
                         'glance_store.s3_store_host',
                         'glance_store.s3_store_bucket']
            }
        },
        'vsphere': {
            'alias': 'glance_store.stores:glance_store._drivers.vmware_datastore.Store'
        },
        'glance_store._drivers.vmware_datastore.Store': {
            'endpoint': {
                'name': ['%s/%s',
                         'glance_store.vmware_server_host',
                         'glance_store.vmware_datastore_name'
                         ],
                'connection': {
                    'glance_store.vmware_api_insecure': 'glance_store.vmware_api_insecure',
                    'glance_store.vmware_api_retry_count': 'glance_store.vmware_api_retry_count',
                    'glance_store.vmware_datacenter_path': 'glance_store.vmware_datacenter_path',
                    'glance_store.vmware_datastore_name': 'glance_store.vmware_datastore_name',
                    'glance_store.vmware_server_host': 'glance_store.vmware_server_host',
                    'glance_store.vmware_server_password': 'glance_store.vmware_server_password',
                    'glance_store.vmware_server_username': 'glance_store.vmware_server_username',
                    'glance_store.vmware_store_image_dir': 'glance_store.vmware_store_image_dir',
                    'glance_store.vmware_task_poll_interval': 'glance_store.vmware_task_poll_interval'
                }
            },
            'device': {
                'name': ['VMWare Image backend %s/%s',
                         'glance_store.vmware_server_host',
                         'glance_store.vmware_datastore_name'
                         ]
            }
        }
    }
}

_DRIVERS = {
    'sqlalchemy': {
        'type': 'database',
        'extra': {
            'url': 'https://pypi.python.org/pypi/SQLAlchemy',
            'python_class': 'sqlalchemy',
            'version': '0.9.8',
            'device_support': [
                {
                    'vendor': 'MYSQL',
                    'model': 'MYSQL',
                    'version': ['5.6','5.7']
                }
            ],
            'configuration_guide':'',
            'metadata': {
                'wiki': ''
            }
        }
    },
    'rabbit': {
        'type': 'message',
        'extra': {
            'url': 'https://github.com/openstack/oslo.messaging',
            'python_class': '%{service_type}s.openstack.common.rpc.impl_kombu',
            'version': '0.9.8',
            'device_support': [
                {
                    'vendor': 'RabbitMQ',
                    'model': 'RabbitMQ Server',
                    'version': ['3.4','3.5']
                }
            ],
            'configuration_guide':'',
            'metadata': {
                'wiki': ''
            }
        }
    },
    'vmwareapi.VMwareVCDriver': {
        'type': 'nova',
        'class': 'hypervisor',
        'extra': {
            'url': 'https://github.com/openstack/nova',
            'python_class': 'nova.virt.vmwareapi.VMwareVCDriver',
            'version': '2014.5',
            'device_support': [
                {
                    'vendor': 'VMWare',
                    'model': 'vSphere',
                    'version': ['5.0','5.1']
                }
            ],
            'configuration_guide':'',
            'metadata': {
                'wiki': ''
            }
        }
    },
    'libvirt.LibvirtDriver': {
        'type': 'nova',
        'class': ['hypervisor', 'container'],
        'extra' : {
            'url': 'https://github.com/openstack/nova',
            'python_class': 'nova.virt.libvirt.LibvirtDriver',
            'version': '2014.5',
            'device_support': [
                {
                    'vendor': 'KVM, LXC, QEMU, UML, and XEN',
                    'model': 'KVM',
                    'version': ['5.0','5.1']
                }
            ],
            'configuration_guide':'',
            'metadata': {
                'libvirt_supports': 'https://wiki.openstack.org/wiki/LibvirtDistroSupportMatrix'
            }
        }
    },
    'nova.virt.hyperv.driver.HyperVDriver': {
        'type': 'nova',
        'extra' : {
            'url': 'https://github.com/openstack/nova',
            'python_class': 'nova.virt.hyperv.driver.HyperVDriver',
            'version': '2014.5',
            'device_support': [
                {
                    'vendor': 'Microsoft',
                    'model': 'Hyper-V',
                    'version': ['2014']
                }
            ],
            'configuration_guide':'',
            'metadata': {
            }
        }
    },
    'cinder.volume.drivers.lvm.LVMISCSIDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.lvm.LVMISERDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARFCDriver': {
        'type': 'cinder',
        'class': 'volume',
        'requirements_txt': {
        #     TODO(mrkanag) Add installer reqs here, pip pkg or apt pkg or
        #     any other OS packages
        },
        'apt_get_list': {

        },
        'deprecation': {
            'alternate': '',
            'since': '2012.1'
        }
    },
    'cinder.volume.drivers.san.hp.hp_lefthand_iscsi.HPLeftHandISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.coraid.CoraidDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.eqlx.DellEQLSanISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.emc.emc_vmax_iscsi.EMCVMAXISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.emc.emc_vmax_fc.EMCVMAXFCDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.emc.emc_cli_iscsi.EMCCLIISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.glusterfs.GlusterfsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.hds.iscsi.HDSISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.hds.nfs.HDSNFSDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.hds.hds.HUSDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.hitachi.hbsd_fc.HBSDFCDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.hitachi.hbsd_iscsi.HBSDISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.san.hp.hp_msa_fc.HPMSAFCDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.huawei.HuaweiVolumeDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.ibm.gpfs.GPFSDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.ibm.storwize_svc.StorwizeSVCDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.xiv_ds8k.XIVDS8KDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.netapp.common.NetAppDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.netapp.iscsi.NetAppDirectCmodeISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.netapp.nfs.NetAppDirectCmodeNfsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.netapp.iscsi.NetAppDirect7modeISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.netapp.nfs.NetAppDirect7modeNfsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.nexenta.iscsi.NexentaISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.nexenta.nfs.NexentaNfsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.nfs.NfsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.prophetstor.dpl_fc.DPLFCDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.prophetstor.dpl_iscsi.DPLISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.pure.PureISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.sheepdog.SheepdogDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.solidfire.SolidFireDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.vmware.vmdk.VMwareVcVmdkDriver': {
        'type': 'cinder',
        'class': 'volume',
        'compute_driver': 'vmwareapi.VMwareVCDriver'
    },
    'cinder.volume.drivers.windows.WindowsDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.xenapi.sm.XenAPINFSDriver': {
        'type': 'cinder',
        'class': 'volume'
    },
    'cinder.volume.drivers.zadara.ZadaraVPSAISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.volume.drivers.zfssa.zfssaiscsi.ZFSSAISCSIDriver': {
        'type': 'cinder',
        'class': 'volume',
        'protocol': 'iSCSI'
    },
    'cinder.backup.drivers.ceph': {
        'type': 'cinder',
        'class': 'backup'
    },
    'cinder.backup.drivers.tsm': {
        'type': 'cinder',
        'class': 'backup'
    },
    'cinder.backup.drivers.swift': {
        'type': 'cinder',
        'class': 'backup'
    },
    'cinder.zonemanager.drivers.brocade.brcd_fc_zone_driver.BrcdFCZoneDriver':
    {
        'type': 'cinder',
        'class': 'zone_manager'
    },
    'cinder.zonemanager.drivers.cisco.cisco_fc_zone_driver.CiscoFCZoneDriver':
    {
        'type': 'cinder',
        'class': 'zone_manager'
    },
    'glance_store._drivers.filesystem.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.http.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.cinder.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.swift.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.rbd.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.gridfs.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.vmware_datstore.Store': {
        'type': 'glance'
    },
    'glance_store._drivers.filesystem.Store': {
        'type': 'glance'
    },
    'neutron.agent.linux.interface.OVSInterfaceDriver': {
        'type': 'neutron'
    },
    'neutron.agent.linux.dhcp.Dnsmasq': {
        'type': 'neutron'
    },
    'neutron.agent.linux.interface.OVSInterfaceDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.mech_linuxbridge.LinuxbridgeMechanismDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.mech_openvswitch.OpenvswitchMechanismDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.type_local.LocalTypeDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.type_flat.FlatTypeDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.type_vlan.VlanTypeDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.type_gre.GreTypeDriver': {
        'type': 'neutron'
    },
    'neutron.plugins.ml2.drivers.type_vxlan.VxlanTypeDriver': {
        'type': 'neutron'
    },
    'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver': {
        'type': 'neutron'
    },
    'nova.virt.firewall.NoopFirewallDriver' : {
        'type': 'neutron'
    },
    'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver': {
        'type': 'neutron'
    }
}


def get_drivers_config():
    return _DRIVERS_CONFIG


def get_drivers_def():
    return _DRIVERS
