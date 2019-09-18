### Author: Tamas Plugor EMEA TAC
### Date: 2019-06-18
### Demo script to remove a configlet from a device and generate a task

import cvp
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

host = '10.83.13.33'
port = 443
tmpDir=''

d = cvp.Cvp(host,True,port,tmpDir)
d.authenticate('cvpadmin','arastra')
dev1 = d.getDevice('44:4c:a8:25:dc:41', provisioned=True)

# save the configlet object in a variable
cfg = d.getConfiglet('vlan1444')

# provide the device and the list of configlet objects to be removed
d.removeConfigletAppliedToDevice(dev1,[cfg])

# This will generate a task, it will return the taskID in a list
#[u'1030']


## This gives you the list of configlets under that device
## dev1.configlets
#[u'aaa_policy', u'vrf_management', u'prompt', u'management_api', u'snmp_basics', u'time_config', u'user_accounts', u'aliases', u'event_cli_bootstrap', u'shannon_syslog', u'shannon_routes', u'up380_10.83.13.132_unique', u'JPE15470679lldp_int_desc', u'vlan 50', u'vlan1444', u'RECONCILE_10.83.13.132']
#
