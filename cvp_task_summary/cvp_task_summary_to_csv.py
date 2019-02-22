#!/usr/bin/env python
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
#
# Version 1.0 22/02/2019
#
# Written by:
#      Tamas Plugor, Arista Networks
#
# Tool to export all task ids as a CSV
#


# Import Required Libraries
import ssl
import sys
#sys.path.append('/usr/local/lib/python2.7/site-packages')
import argparse
import getpass
import requests
import json
import csv
import time
from requests import packages
from jsonrpclib import Server
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

# Set up classes to interact with CVP API
# serverCVP exception class

class serverCvpError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Create a session to the CVP server
class serverCvp(object):

    def __init__ (self,HOST,USER,PASS):
        ''' Create session to the host, ignoring any certificate errors'''
        self.url = "https://%s"%HOST
        self.authenticateData = {'userId' : USER, 'password' : PASS}
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        except packages.urllib3.exceptions.ProtocolError as e:
            if str(e) == "('Connection aborted.', gaierror(8, 'nodename nor servname provided, or not known'))":
                raise serverCvpError("DNS Error: The CVP Server %s can not be found" % CVPSERVER)
            elif str(e) == "('Connection aborted.', error(54, 'Connection reset by peer'))":
                raise serverCvpError( "Error, connection aborted")
            else:
                raise serverCvpError("Could not connect to Server")

    def logOn(self):
        '''Calls authentication API and traps any issues, also generates the session cookies required'''
        try:
            headers = { 'Content-Type': 'application/json' }
            loginURL = "/web/login/authenticate.do"
            response = requests.post(self.url+loginURL,json=self.authenticateData,headers=headers,verify=False)
            if "errorMessage" in str(response.json()):
                text = "Error log on failed: %s" % response.json()['errorMessage']
                raise serverCvpError(text)
        except requests.HTTPError as e:
            raise serverCvpError("Error HTTP session to CVP Server: %s" % str(e))
        except requests.exceptions.ConnectionError as e:
            raise serverCvpError("Error connecting to CVP Server: %s" % str(e))
        except:
            raise serverCvpError("Error in session to CVP Server")
        self.cookies = response.cookies
        return response.json()

    def logOut(self):
        '''Clears sessions with CVP server using the session cookies'''
        print "LogOut"
        headers = { 'Content-Type':'application/json' }
        logoutURL = "/cvpservice/login/logout.do"
        response = requests.post(self.url+logoutURL, cookies=self.cookies, json=self.authenticateData,headers=headers,verify=False)
        return response.json()


    def getTasks(self):
        '''get the Task list in json'''
        headers = { 'Content-Type': 'application/json'}
        getURL = "/cvpservice/task/getTasks.do?"
        getParams= {'startIndex':'0', 'endIndex':'0'}
                    
        response = requests.get(self.url+getURL,cookies=self.cookies,params=getParams,verify=False)
        return response.json()


def parseArgs():
   parser = argparse.ArgumentParser( description='CVP test AAA Server connectivtity' )
   parser.add_argument( '--host', default='localhost',
                        help='Hostname or IP address of cvp' )
   parser.add_argument( '--user', required=True, help='Cvp user username' )
   parser.add_argument( '--port', default=443, help='Cvp web-server port number' )
   parser.add_argument( '--ssl', choices=[ 'true', 'false' ], default='true',
                        type=str.lower, help='Connect via HTTPS' )
   parser.add_argument( '--password', default=None, help='password corresponding to'
                        ' the username' )
   args = parser.parse_args()
   args.port = int( args.port )
   return checkArgs( args )

def askPass( user, host ):
   prompt = "Password for user {} on host {}: ".format( user, host )
   password = getpass.getpass( prompt )
   return password

def checkArgs( args ):
   '''check the correctness of the input arguments'''
   if args.password is None:
      args.password = askPass( args.user, args.host )
   return args
def time_converter(unixtime):
 ts = int(unixtime)/1000
 return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def createCSV(dict):
    '''build the CSV from the returned json'''
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = 'tasks' + timestr + '.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = ['Task ID', 'Tagged CC', 'MAC Address', 'Description', 'Host Name', 'IP Address', 
        'Container', 'Created On', 'Created By', 'Executed On', 'Executed By', 'Notes', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        print "Tasks are getting written to CSV"
        for key in dict['data']:
            writer.writerow({'Task ID': key['workOrderId'], 
                            'Tagged CC': key['ccId'], 
                            'MAC Address': key['netElementId'], 
                            'Description': key['description'], 
                            'Host Name': key['workOrderDetails']['netElementHostName'], 
                            'IP Address': key['workOrderDetails']['ipAddress'], 
                            'Container': key['newParentContainerName'], 
                            'Created On': time_converter(key['createdOnInLongFormat']), 
                            'Created By': key['createdBy'], 
                            'Executed On': time_converter(key['executedOnInLongFormat']), 
                            'Executed By': key['executedBy'], 
                            'Notes': key['note'], 
                            'Status': key['workOrderUserDefinedStatus'],
                            })
        print "CSV file {} has been generated in your local directory".format(filename)

def main( ):
    # Get CLI options
    options = parseArgs()
    print"Connecting to %s" %options.host
    # Connecting to CVP
    try:
      cvpSession = serverCvp(options.host,options.user,options.password)
      logOn = cvpSession.logOn()
    except serverCvpError as e:
      print"  Connnection to %s:%s" %(options.host,e.value)
    # Call task exporter
    createCSV(cvpSession.getTasks())       
    cvpSession.logOut

if __name__ == '__main__':
   retval = main()
   sys.exit( retval )