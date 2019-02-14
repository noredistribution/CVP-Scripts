#!/usr/bin/env python

# disable SSL verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import json
import requests
from pprint import pprint as pp

cvpIP = 'https://<CVP_IP>'

headers = { 'Content-Type': 'application/json'}

# login API - you will need to login first
# and save the credentials in a cookie
loginURL = "/web/login/authenticate.do"

# cvp user and password
USER = '<CVP USERNAME>'
PASSWORD = '<CVP PASSWORD>'

# First we have to login and save the session in a cookie
# which can be later referred to make API calls
response = requests.post(cvpIP+loginURL,json={'userId':USER,'password':PASSWORD},headers=headers,verify=False)
cookies = response.cookies

#rest API uri
restAPI = '/api/v1/rest/'

# Serial number of the switch
dataset = 'JPE17471508'

# Sysdb path for temperature values for QSFP in Ethernet49
dom49 = "/Sysdb/environment/archer/temperature/status/system/DomTemperatureSensor49"

# Make the API call
response = requests.get(cvpIP+restAPI+dataset+dom49,cookies=cookies, verify=False)

# print the returned json file
pp(response.json())
