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
# Author: Tamas Plugor
# Date: 2019-09-11
# Proof of Concept

import json
from datetime import datetime
import requests
from flask import Flask, request, abort
import argparse
import sys
import copy

app = Flask(__name__)

# ask for MS Teams webhook URL argument and exit the program if it is not given
parser = argparse.ArgumentParser()
parser.add_argument('--teamsURL', required=True, help="MS teams webhook URL")
if len(sys.argv) < 2:
    parser.print_help(sys.stderr)
    sys.exit(1)        
args = parser.parse_args()

teamsUrl = args.teamsURL

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print request.json
        data2 = request.get_json()
        headers = {
            "content-type": "application/json"
        }
        
        # init card format for MS teams
        teamsdata = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "",
            "sections": [
            ]
        }

        teamsdata_section = {
            "activityTitle": "",
            "activitySubtitle": "",
            "activityImage": "https://repository-images.githubusercontent.com/197042746/81e45880-0678-11eb-9423-a91dce14f372",
            "activityImageType": "article",
            "facts": [{
                "name": "Description",
                "value": ""
            }, {
                "name": "Started",
                "value": ""
            }, {
                "name": "Source",
                "value": ""
            }],
            "markdown": True
        }
        
        # in case we have multiple alerts we have to treat each of them
        for alert_id, alert in enumerate(data2['alerts']):

            teamsdata['sections'].append(copy.deepcopy(teamsdata_section))

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
            
            teamsdata['sections'][alert_id]['activityTitle'] = u'**1 {} events for: {} {} {}** \n Events in this group:'.format(event_status,hostname, sn, event_type)

            alert_title = alert['annotations']['title']
            
            # setting emoji for severities

            emoji = ""
            if sev == "CRITICAL":
                emoji = u"\uD83D\uDD25"
            elif sev == "WARNING":
                emoji = u"\u26A0\uFE0F"
            elif sev == "INFO":
                emoji = u"\u2139"
            elif sev == "ERROR":
                emoji = u'\uD83D\uDED1'

            teamsdata["summary"] = "CVP Event Alert"
            
            # add the titles for all alerts
            teamsdata["sections"][alert_id]["activitySubtitle"] = u'**[{}]** {} {}, {} ({})'.format(sev, emoji, alert_title, sn, hostname)

            args = {
                            'arg0': alert['annotations']['description'],
                            'arg1': date.day,
                            'arg2': month,
                            'arg3': date.year,
                            'arg4': date.hour,
                            'arg5': date.minute,
                            'arg6': date.second,
                            'arg7': alert['generatorURL']
                            }
            # Set description
            teamsdata["sections"][alert_id]["facts"][0]['value']= args['arg0']
            # Set start time
            teamsdata["sections"][alert_id]["facts"][1]['value']= "Started: {arg1} {arg2} {arg3} {arg4}:{arg5}:{arg6}".format(**args)
            # Set URL
            teamsdata["sections"][alert_id]["facts"][2]['value'] = "[{}]({})".format(args['arg7'],args['arg7'])
            

            print teamsdata
        data5 = json.dumps(teamsdata)
        r = requests.post(teamsUrl, data=data5, headers=headers)
        return ""
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5001',debug=True)
