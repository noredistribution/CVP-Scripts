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
# Tool to export all inventory related elements as a CSV
# works with CVP version 2018.2.x


# disable SSL verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
import requests
import time
import csv
from datetime import datetime
from pprint import pprint as pp
from getpass import getpass

cvpIP = 'https://' + raw_input('CVP IP: ')

headers = { 'Content-Type': 'application/json'}

# login API - you will need to login first
# and save the credentials in a cookie
loginURL = "/web/login/authenticate.do"

# cvp user and password
USER = raw_input('CVP username: ')
PASSWORD = getpass()

# First we have to login and save the session in a cookie
# which can be later referred to make API calls
response = requests.post(cvpIP+loginURL,json={'userId':USER,'password':PASSWORD},headers=headers,verify=False)
cookies = response.cookies

#rest API uri
restAPI = '/api/v1/rest/'

# Path for EosSwitches
path = 'analytics/DatasetInfo/EosSwitches'

# Make the API call
response = requests.get(cvpIP+restAPI+path,cookies=cookies, verify=False)

# print the returned json file
inventory = response.json()

def createCSV(dict):
    '''build the CSV from the returned json'''
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = 'inventory' + timestr + '.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = ['Device', 'Status', 'Model', 'EOS', 'TerminAttr', 
        'MAC Address', 'Serial Number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        print "Inventory is getting written to CSV"
        for key in dict['notifications']:

            # Path for system MAC
            sysmacpath = '/Sysdb/hardware/entmib'
            dataset = key['updates'].values()[0]['key']
            print "dateset is:", dataset
            # make API call to get the system MAC for the dataset
            response2 = requests.get(cvpIP + restAPI + dataset + sysmacpath, cookies=cookies, verify=False)
            response2 = response2.json()
            # print "Dataset ID: {}".format(dataset)
            # pp(response2)
            
            for i in response2['notifications']:
                if 'systemMacAddr' in i['updates']:
                    mac_addr = i['updates']['systemMacAddr']['value']
            
            # getting the model name
            # the path is different for modular vs fixed
            if 'fixedSystem' in response2['notifications'][0]['updates']:
                modeltype = '/fixedSystem'
            else:
                modeltype = '/chassis'
            
            response3 = requests.get(cvpIP + restAPI + dataset + sysmacpath + modeltype, cookies=cookies, verify=False)
            response3 = response3.json()
            # pp(response3)
            for mdl in response3['notifications']:
                if 'modelName' in mdl['updates']:
                    model = mdl['updates']['modelName']['value']
            # populating the rows
            writer.writerow({'Device': key['updates'].values()[0]['value']['hostname'], 
                            'Status': key['updates'].values()[0]['value']['status'],
                            'Model': model,
                            'EOS': key['updates'].values()[0]['value']['eosVersion'],
                            'TerminAttr': key['updates'].values()[0]['value']['terminAttrVersion'],
                            'MAC Address': mac_addr,
                            'Serial Number': dataset
                            })
        print "CSV file {} has been generated in your local directory".format(filename)

createCSV(inventory)
