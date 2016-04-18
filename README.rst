=========================
namos - OpenStack manager
=========================

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/namos
* Source: http://git.openstack.org/cgit/openstack/namos
* Bugs: http://bugs.launchpad.net/soman
* Wiki: https://wiki.openstack.org/wiki/Namos

Features
--------

* Automatic discovery of OpenStack deployment architecture

How to setup db
----------------
* create the 'namos' db using below command

  `create database namos`

* update database.connection in /etc/namos/namos.conf with db username and
  password

* Run the below command to sync the namos schema

  `namos-manage create_schema`

How to setup namos
------------------
* Assume, namos is cloned at /opt/stack/namos, then run below command to
  install namos from this directory.

  `sudo python setup.py install`

How to run namos
-----------------
* namos-api - Namos API starts to listen on port 9999. Now it does have support
  for keystone authendication

  `namos-api`

* namos-manager - Namos backend service, to configured the number of workers,
  update os_manager->workers

 `namos-manager --config-file=/etc/namos/namos.conf`

NOTE: Before running the namos-manager, please add os-namos agent in the
console scripts of respective service components.

To find the 360 view of OpenStack deployment
--------------------------------------------
Run http://localhost:9999/v1/view_360

It provides 360 degree view under region->service_node in the response. In
addition, gives the current live status of each servicec components.

To find the status of components
--------------------------------
Run the below command

`namos-manage status`

NOTE: This command supports to query status based on given node name, node type
, service and component. To find more details run this command with --help