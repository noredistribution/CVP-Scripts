#!/usr/bin/env python
# Author: Tamas Plugor (TAC-EMEA)
# Date: 2019-06-04
# small hackathon project to automate adding dispatcher on a multinode cluster
# tested on Foster

import os
import yaml
import subprocess
import paramiko
import copy
import time
from getpass import getpass
from shutil import copyfile

# How to add firewall rules via CLI
# sudo firewall-cmd --zone=public --add-rich-rule 'rule family="ipv4" source address="172.28.161.168" port port="9931" protocol="tcp" accept' --permanent && firewall-cmd --reload
# sudo firewall-cmd --zone=public --add-rich-rule 'rule family="ipv4" source address="172.28.161.169" port port="9931" protocol="tcp" accept' --permanent && firewall-cmd --reload
# sudo firewall-cmd --zone=public --add-rich-rule 'rule family="ipv4" source address="172.28.161.170" port port="9931" protocol="tcp" accept' --permanent && firewall-cmd --reload

# ask for the root password
print "Please type the root password:"
password = getpass()

def copyandrestartfwd(nodeIP):
   # establish SSH session to remote node
   p = paramiko.SSHClient()
   p.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   p.connect(nodeIP, username="root", password=password)
   
   # copy the public.xml file
   fwdpath='/etc/firewalld/zones/public.xml'
   sftp = p.open_sftp()
   sftp.put(fwdpath,fwdpath)
   sftp.put(filepath,filepath)
   sftp.close()
   
   #restart
   stdin, stdout, stderr = p.exec_command("service firewalld restart")

def addRule(nodeIP):
   # Adding the rules to Firewalld's public.xml
   #fwcmd = 'sudo firewall-cmd --zone=public --add-rich-rule'
   #rule = 'rule family="ipv4" source address="%s" port port="%d" protocol="tcp" accept'
   #fwrld = 'sudo firewall-cmd --reload'
   fwcmdl = ['sudo', 'firewall-cmd', '--zone=public', '--add-rich-rule', '\'rule', 'family="ipv4"', 
             'source', 'address="%s"'% nodeIP, 'port', 'port="%d"' % (ports['dispatcher'] + cntrno), 'protocol="tcp"', 'accept\'', 
             ' --permanent', ' && ', 'sudo', 'firewall-cmd', '--reload']
   fwcommand = 'sudo firewall-cmd --zone=public --add-rich-rule \'rule family="ipv4" source address="%s" port port="%d" protocol="tcp" accept\'  --permanent && sudo firewall-cmd --reload' %  (nodeIP, ports['dispatcher'] + cntrno)
   process = subprocess.check_output(fwcommand, shell=True)
   #output, error = process.communicate()
   #print output

# get the Nodes
# keys will be: PRIMARY_DEVICE_INTF_IP, SECONDARY_DEVICE_INTF_IP, TERTIARY_DEVICE_INTF_IP

nodes = {}

for x in os.environ:
   if "INTF_IP" in x:
      nodes[x] = os.environ[x]


filepath = "/cvpi/conf/components/aeris.multinode.yaml"
backup = "/cvpi/conf/components/aeris.multinode.yaml.bkp"

# backup the yaml file
copyfile(filepath, backup)

with open(filepath, 'r') as f:
 f = yaml.load(f)

# determine number of current dispatchers in the bundle
cntrlst = [x for x in f['aeris']['bundle'] if 'dispatcher' in x]
cntrno = len(cntrlst)

# Define the base ports numbers
ports = {'debug': 6064, 'dispatcher': 9930}

# Define variables that will change

expvars = 'http://localhost:{}/debug/vars'

goroutines = 'http://localhost:{}/debug/pprof/goroutine?debug=2'

monitor = "-monitor=0.0.0.0:{}"

addr = '-addr=${CVP_CURRENT_HOSTNAME}:%d'

process = '^${CVP_HOME}/apps/aeris/bin/dispatcher .*:%d.*'

logfiles = '${CVP_HOME}/apps/aeris/logs/dispatcher-%d.std*.log'

pidfile = '/var/run/cvpi/dispatcher-%d.pid'

# creat new dispatcher key

newdispatcher = 'dispatcher-%d' % (cntrno+1)
f[newdispatcher] = copy.deepcopy(f['dispatcher-2'])

# changing the monitor and dispatcher port for the start action list
for ctr, i  in enumerate(f[newdispatcher]['actions']['start']['command']):
  if 'monitor' in i:
    f[newdispatcher]['actions']['start']['command'][ctr] = monitor.format(ports['debug']+cntrno)
  if 'addr=' in i:
    f[newdispatcher]['actions']['start']['command'][ctr] = addr % (ports['dispatcher']+cntrno)
  if 'dispatcher-2' in i:
  	f[newdispatcher]['actions']['start']['command'][ctr] = newdispatcher

# changing the expvars, goroutines port, the dispatcher port and pidfile in debug and status dicts
f[newdispatcher]['debug']['expvars'][-1] = expvars.format(ports['debug']+cntrno)
f[newdispatcher]['debug']['goroutines'][-1] = goroutines.format(ports['debug']+cntrno)
f[newdispatcher]['status']['process'] = process % (ports['dispatcher']+cntrno)
f[newdispatcher]['status']['pidfile'] = pidfile % ( cntrno + 1 )
f[newdispatcher]['actions']['stop']['command'][-1] = newdispatcher

# changing the log file name
f[newdispatcher]['logfiles'][0] = logfiles % ( cntrno + 1 )

# Add new dispatcher to the aeris bundle
f['aeris']['bundle'][newdispatcher] = None

f['aerisinitv2g']['actions']['reset']['deps'][newdispatcher] = 'stop'

with open('/cvpi/conf/components/aeris.multinode.yaml', 'w') as outfile:
   yaml.dump(f, outfile, default_flow_style=False)


# add the rules for all nodes

for node in nodes:
  print "Adding rule for %s" % (nodes[node])
  addRule(nodes[node])  

# copy the public.xml over to the other nodes
print "Copying public.xml and aeris.multinode.yaml to node2..."
print "and restarting firewalld"
copyandrestartfwd(nodes['SECONDARY_DEVICE_INTF_IP'])

print "Copying public.xml and aeris.multinode.yaml to node3..."
print "and restarting firewalld"
copyandrestartfwd(nodes['TERTIARY_DEVICE_INTF_IP'])

# stop aeris
process = subprocess.Popen("su - cvp -c 'cvpi stop aeris'", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()
print stderr

# start aeris
process = subprocess.Popen("su - cvp -c 'cvpi start aeris'", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()
print stderr

# check the status of aeris
process = subprocess.Popen("su - cvp -c 'cvpi status aeris'", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()
print stdout

# wait 5 seconds and check kafka lag output
print "Sleeping for 5 seconds"
time.sleep(5)

print "Showing output of postDB consumers"
print "-"*80
kafkalag = "/cvpi/apps/aeris/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 127.0.0.1:9092 --describe --group postDB_dispatcher"

process = subprocess.Popen(kafkalag, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()
print stdout
print "-"*80
print "\n"
print "If the formatting above is off, please run the following command to check the consumers"
print "and check if there are as many unique IDs as the number of dispatchers in total"
print "\n"
print "/cvpi/apps/aeris/kafka/bin/kafka-consumer-groups.sh --bootstrap-server 127.0.0.1:9092 --describe --group postDB_dispatcher"
print "\n"
