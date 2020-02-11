#!/usr/bin/env python

# disable SSL verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import json
import requests
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from pprint import pprint as pp

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
   print ('calling url: ', url)
   return requests.get( url, cookies=cookies, verify=False )

def authenticate( cvpName, loginInfo ):
   url = 'https://%s:443/web/login/authenticate.do' % ( cvpName, )
   return requests.post( url, json.dumps( loginInfo ), verify=False )

def getPendingCC(cvpName):
   api = 'changecontrol/pending'
   url = 'https://%s/api/v1/rest/cvp/%s' % ( cvpName, api )
   print('calling url: ', url)
   return requests.get( url, cookies=cookies, verify=False )

def getCompletedCC(cvpName):
   api = 'changecontrol/runnability'
   url = 'https://%s/api/v1/rest/cvp/%s' % ( cvpName, api )
   print('calling url: ', url)
   return requests.get( url, cookies=cookies, verify=False )

def getCCList(cvpName):
   api = 'changecontrol/status'
   url = 'https://%s/api/v1/rest/cvp/%s' % ( cvpName, api )
   print ('calling url: ', url)
   return requests.get( url, cookies=cookies, verify=False )

def getCCIdStatus(cvpName,ccID):
   api = 'changecontrol/status'
   url = 'https://%s/api/v1/rest/cvp/%s/%s/all' % ( cvpName, api, ccID )
   print ('calling url: ', url)
   return requests.get( url, cookies=cookies, verify=False )

if __name__ == '__main__':
    urllib3.disable_warnings()
    cvpName, loginInfo  = parseArgs()
    cookies = authenticate( cvpName, loginInfo ).cookies
    #print json.loads(getCvpInfo( cvpName ).text)
    #print getCvpInfo( cvpName ).json()

    print ('getCvpInfo:')
    print (json.dumps(getCvpInfo( cvpName ).json(), indent=2))



    # Menu
    while True:
        try:
            print('+','-'*78,'+')
            print('Choose an action from below:')
            print('\n')
            print('1) Get Pending Change Controls')
            print('2) Get Completed Change Controls')
            print('3) Get full list of Change Controls')
            print('4) Get the status of a Change Control')
            print('+','-'*78,'+')
            print('\n')
            action = input('Enter action:')
            if action == "1":
                # GET Pending CCs
                print ('Get Pending CCs:')
                print (json.dumps(getPendingCC( cvpName ).json(), indent=2))
            if action == "2":
                # GET Completed CCs
                print ('Get Completed CCs:')
                print (json.dumps(getCompletedCC( cvpName ).json(), indent=2))
            if action == "3":
                # GET CC list
                print ('Get CC list:')
                print (json.dumps(getCCList( cvpName ).json(), indent=2))
            elif action == "4":
                # Get status of a CC
                ccID = str(input('Enter CC ID:'))
                print (json.dumps(getCCIdStatus( cvpName, ccID ).json(), indent=2))
            else:
                    print ('invalid action:', action)
        except KeyboardInterrupt:
            print ('exiting..')
            break


