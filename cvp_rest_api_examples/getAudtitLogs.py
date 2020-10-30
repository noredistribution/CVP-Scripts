#!/usr/bin/env python
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
# Author: Tamas Plugor
# Date: 2020-10-30
# Version: 0.1
# Proof of concept audit log exporter to syslog
import requests
import json
import argparse
import urllib3
import syslog
from datetime import datetime
import time

def timehr(ts):
    return datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')
def parseArgs():
   parser = argparse.ArgumentParser()
   parser.add_argument( '-c', '--cvpName', required=True, help='cvp name' )
   parser.add_argument( '-u', '--userId', help='username',
           default='cvpadmin')
   parser.add_argument( '-p', '--password', help='password',
           default='arastra')
   args = vars( parser.parse_args() )
   return args.pop( 'cvpName' ), args

def getCvpInfo( cvpName ):
   api = 'cvpInfo/getCvpInfo.do'
   url = 'https://%s:443/web/%s' % ( cvpName, api )
   print 'calling url: ', url
   return requests.get( url, cookies=cookies, verify=False )

def getAuditLogs( cvpName, start, end):
   api = 'audit/getLogs.do'
   url = 'https://%s:443/cvpservice/%s' % ( cvpName, api )
   body = {"category":"USER",
           "dataSize": 1000,
           "startTime": start,
           "endTime": end,
           "objectKey": "cvpadmin"
        }
   print 'calling url: ', url
   #response = [json.dumps()]
   return requests.post( url, cookies=cookies, data=json.dumps(body), verify=False )

def authenticate( cvpName, loginInfo ):
   url = 'https://%s:443/web/login/authenticate.do' % ( cvpName, )
   return requests.post( url, json.dumps( loginInfo ), verify=False )

if __name__ == '__main__':
    urllib3.disable_warnings()
    cvpName, loginInfo  = parseArgs()
    cookies = authenticate( cvpName, loginInfo ).cookies

    print 'getCvpInfo:'
    print json.dumps(getCvpInfo( cvpName ).json(), indent=2)

    while True:
        # set end time to the currnet time
        end = int(time.time()*1000.0)
        # set start time to 1 hour before end time
        start = end - 3600000
        auditLogs = getAuditLogs( cvpName, start, end ).json()
        for i in auditLogs['data']:
            log = i['userName'] + ' ' + i['activity'] + ' at ' + timehr(i['dateTimeInLongFormat'])
            syslog.syslog(syslog.LOG_INFO, log)
        time.sleep(3601)

