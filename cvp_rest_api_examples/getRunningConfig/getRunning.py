#!/usr/bin/env python
#
# Copyright (c) 2020, Arista Networks, Inc.
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
# Running-Config Transfer for CVP
#
#    Version 0.9 07/05/2020
#
#    Initial script Written by:
#       Hugh Adams, Arista Networks
#    Modified by Tamas Plugor, Arista Networks
#

import argparse
import getpass
import sys
import json
import requests
from requests import packages
from datetime import datetime

# CVP manipulation class

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
        headers = { 'Content-Type':'application/json' }
        logoutURL = "/cvpservice/login/logout.do"
        response = requests.post(self.url+logoutURL, cookies=self.cookies, json=self.authenticateData,headers=headers,verify=False)
        return response.json()

    def getDeviceHostName(self):
        # Get the device hostnames for the serialNumbers
        getURL = "/cvpservice/inventory/devices?"
        getParams = {"provisioned":"false"}
        response = requests.get(self.url+getURL,cookies=self.cookies,params=getParams,verify=False)
        if "errorMessage" in str(response.json()):
            text = "Error getSnapshot data failed: %s" % response.json()['errorMessage']
            raise serverCvpError(text)
        return response.json()

    def getRunningConfig(self,deviceId):
        getURL = "/cvpservice/snapshot/deviceConfigs/"+deviceId+"?current=true"
        try:
            response = requests.get(self.url+getURL,cookies=self.cookies,verify=False)
            if "errorMessage" in str(response.json()):
                text = "Running-config not found for {}: {}".format(deviceId, response.json()['errorMessage'])
                raise serverCvpError(text)
                print "Running-config not found for {}. The file will be empty.".format(deviceId)
        except serverCvpError:
            pass
            return ""
        return response.json()["runningConfigInfo"]



def parseArgs():
    """Gathers comand line options for the script, generates help text and performs some error checking"""
    usage = "usage: %prog [options] userName password target destPath snapshot"
    parser = argparse.ArgumentParser(description="Fetch Snapshots from CVP")
    parser.add_argument("-c","--cvp",required=True, help='CVP IP address')
    parser.add_argument("-u","--userName",required=True, help='Username to log into CVP')
    parser.add_argument("-p","--password", help='Password for CVP user to login')
    #parser.add_argument("--target", nargs="*", metavar='TARGET', default=[],
    #                    help='List of CVP appliances to get snapshot from URL,URL')
    parser.add_argument("-dst","--destPath",default=None, help='Directory to copy Snapshots to')
    parser.add_argument("--snapshot", default=None, help='Name of snapshot to retrieve')
    args = parser.parse_args()
    return checkArgs( args )

def askPass( user, host ):
    """Simple function to get missing password if not recieved as a CLI option"""
    prompt = "Password for user {} on host {}: ".format( user, host )
    password = getpass.getpass( prompt )
    return password

def checkArgs( args ):
    '''check the correctness of the input arguments'''
    # Set Intial Variables required
    getCvpAccess = False
    destList = []

    # React to the options provided
    # Directory to copy Snapshot files to
    if args.destPath == None:
        args.destPath = raw_input("Destination Backup Directory Path: ")
    # CVP Username for script to use
    if args.userName == None:
        getCvpAccess = True

    # CVP Password for script to use
    if args.password == None:
        getCvpAccess = True
    else:
        if (args.password[0] == args.password[-1]) and args.password.startswith(("'", '"')):
            password = args.password[1:-1]

    if getCvpAccess:
        args.userName = raw_input("User Name to Access CVP: ")
        args.password = askPass( args.userName, "CVP" )

    return args


def main():
    # Get CLI Options
    options = parseArgs()

    # Get SnapShotData from CVP
    print "Retrieving SnapShot from CVP"
    print "Attaching to API on %s to get Snapshot Data" %options.cvp
    try:
        cvpSession = serverCvp(str(options.cvp),options.userName,options.password)
        logOn = cvpSession.logOn()
    except serverCvpError as e:
        text = "serverCvp:(main1)-%s" % e.value
        print text
    print "Login Complete"
    deviceListHostname = cvpSession.getDeviceHostName()
    deviceSerialPair = {}
    i = 0
    for key in deviceListHostname:
        deviceSerialPair[deviceListHostname[i]["serialNumber"]] = deviceListHostname[i]["hostname"]
        i +=1
    #print deviceSerialPair

    runningConfig = {}
    for device in deviceSerialPair:
        #print device, type(device)
        runningConfig[device] = cvpSession.getRunningConfig(device)
        print "Printing running-config for {}".format(device)
        if deviceSerialPair[device] != "":
            rcFile = options.destPath+str(deviceSerialPair[device])+".cfg"
        else:
            rcFile = options.destPath+str(device)+".cfg"
        try:
            fhandle = open(rcFile, 'w')
        except IOError as file_error:
            file_error_text = str("File Open Error:"+str(file_error))
            print file_error_text
        fhandle.write(runningConfig[device])
        fhandle.write("\n")
        fhandle.close()
    print "\n"
    print "="*80
    print "Number of running-configs printed: {}".format(len(deviceSerialPair.keys()))
    print "Check the config files in {}".format(options.destPath)
    print "="*80
    print "Logout from CVP:%s"% cvpSession.logOut()['data']

if __name__ == '__main__':
    main()
