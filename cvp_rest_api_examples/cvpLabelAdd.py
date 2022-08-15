#!/usrb/bin/env python
# Copyright (c) 2019, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF NOT ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#!/usr/bin/env python
import requests
import json
import argparse
import urllib3

def parseArgs():
   parser = argparse.ArgumentParser()
   parser.add_argument( '-c', '--cvpName', required=True, help='cvp name' )
   parser.add_argument( '-u', '--userId', help='username',
           default='arista')
   parser.add_argument( '-p', '--password', help='password',
           default='arista')
   args = vars( parser.parse_args() )
   return args.pop( 'cvpName' ), args

def getCvpInfo( cvpName ):
   api = 'cvpInfo/getCvpInfo.do'
   url = 'https://%s:443/web/%s' % ( cvpName, api )
   print 'calling url: ', url
   return requests.get( url, cookies=cookies, verify=False )

def addDeviceToLabel( cvpName, label, deviceMac ):
   api = 'label/labelAssignToDevice.do'
   url = 'https://%s:443/web/%s' % ( cvpName, api )
   body = {'label': label, 'device': deviceMac}
   print 'calling url: ', url
   return requests.post( url, cookies=cookies, data=json.dumps(body), verify=False )

def authenticate( cvpName, loginInfo ):
   url = 'https://%s:443/web/login/authenticate.do' % ( cvpName, )
   return requests.post( url, json.dumps( loginInfo ), verify=False )

if __name__ == '__main__':
    urllib3.disable_warnings()
    cvpName, loginInfo  = parseArgs()
    cookies = authenticate( cvpName, loginInfo ).cookies
    #print json.loads(getCvpInfo( cvpName ).text)
    #print getCvpInfo( cvpName ).json()

    print 'getCvpInfo:'
    print json.dumps(getCvpInfo( cvpName ).json(), indent=2)
    # ADD DEVICE TO LABEL
    # label = "{ tagType: tagValue }"
    label = "mlag:mlagNY"
    device = "de:ad:be:ef:ca:fe"
    print 'addDeviceToLabel:', label, device
    print json.dumps(addDeviceToLabel( cvpName, label, device ).json(), indent=2)
