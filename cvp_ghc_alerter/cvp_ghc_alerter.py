#!/usr/bin/env python
# Copyright (c) 2019 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,  this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of the Arista nor the names of its contributors may be used to endorse or promote products derived from this software without 
#   specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import json
from datetime import datetime
import requests
from flask import Flask, request, abort
import argparse
import sys


app = Flask(__name__)

# ask for GHC webhook URL argument and exit the program if it is not given
parser = argparse.ArgumentParser()
parser.add_argument('--ghcURL', required=True, help="GHC webhook URL")
if len(sys.argv) < 2:
    parser.print_help(sys.stderr)
    sys.exit(1)        
args = parser.parse_args()

ghcUrl = args.ghcURL

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print request.json
        data2 = request.get_json()
        headers = {
            "content-type": "application/json"
        }

        # init dict for GHC and init the cards key
        # for grouped events we will have multiple alerts
        ghc = {}
        ghc["cards"] = []
        counter = len(data2['alerts'])
        while counter != 0:
          ghc["cards"].append({})
          counter = counter - 1

        # in case we have multiple alerts we have to treat each of them
        for eaid, alert in enumerate(data2['alerts']):

            if alert['status'] == 'firing':
                    event_status = 'new'
            elif alert['status'] == 'resolved':
                    event_status = 'resolved'
            if 'deviceHostname' in alert['labels']:
                    hostname = alert['labels']['deviceHostname']
            elif 'tag_hostname' in alert['labels']:
                    hostname = alert['labels']["tag_hostname"]
            else:
                hostname = ""
            if 'deviceId' in alert['labels']:
                    sn = alert['labels']['deviceId']
            else:
                    sn = ""
            event_type = alert['labels']['eventType']
            sev = alert['labels']['severity']
            startsAt = alert['startsAt']
            date = datetime.strptime(startsAt,'%Y-%m-%dT%H:%M:%SZ')
            month = date.strftime('%b')

            # creating dictionary for GHC's accepted formatting
            ghc['cards'][eaid]['header'] = {}
            ghc['cards'][eaid]['sections'] = []
            ghc['cards'][eaid]['sections'].append({})
            ghc['cards'][eaid]['sections'][0]['widgets'] = []
            ghc['cards'][eaid]['sections'][0]['widgets'].append({})
            ghc["cards"][eaid]["sections"][0]['widgets'][0]['keyValue'] = {}
            ghc["cards"][eaid]["sections"][0]['widgets'][0]['buttons'] = []
            
            if event_status == 'new':
                event_title = "<b><font color=\"#ff0000\">1 {} events for: {} {} {}</font></b>".format(event_status,hostname, sn, event_type)
            elif event_status == "resolved":
                event_title = "<b><font color=\"#0C9503\">1 {} events for: {} {} {}</font></b>".format(event_status,hostname, sn, event_type)
            
            ghc['cards'][eaid]['header']['title'] = event_title
            ghc['cards'][eaid]['header']['subtitle'] = "Events in this group:"
            alert_title = alert['annotations']['title']
            
            # setting emoji for severities
            emoji = ""
            if sev == "CRITICAL":
                emoji = "\uD83D\uDD25"
            elif sev == "WARNING":
                emoji = "\u26A0\uFE0F"
            elif sev == "INFO":
                emoji = "\u2139"
            elif sev == "ERROR":
                emoji = "\uD83D\uDED1"

            # add the titles for all alerts
            ghc_alert = u"<b>[{}]</b> {} {}, {} <b><font color=\"#0000ff\">({})</font></b>".format(sev, emoji, alert_title, sn, hostname)
            
            # create the dictionary with timestamps
            args = {
                            'arg0': alert['annotations']['description'],
                            'arg1': date.day,
                            'arg2': month,
                            'arg3': date.year,
                            'arg4': date.hour,
                            'arg5': date.minute,
                            'arg6': date.second 
                            }

            ghc["cards"][eaid]["sections"][0]['widgets'][0]['keyValue']['content']= ("{} <br>"
            "<b>Description:</b> {arg0}<br>"
            "<b>Started:</b> {arg1} {arg2} {arg3} {arg4}:{arg5}:{arg6}").format(ghc_alert,**args)
            ghc["cards"][eaid]["sections"][0]['widgets'][0]['keyValue']['contentMultiline'] = 'true'


            ghc['cards'][eaid]['sections'][0]['widgets'][0]["buttons"] = [
                    {
                      "textButton": {
                        "text": "Open event",
                        "onClick": {
                          "openLink": {
                            "url": alert['generatorURL']
                          }
                        }
                      }
                    }
                  ]

            print ghc
        resp = json.dumps(ghc)
        r = requests.post(ghcUrl, data=resp, headers=headers)
        return ""
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5001',debug=True)
