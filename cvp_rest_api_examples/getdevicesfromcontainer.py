import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from pprint import pprint as pp
cvpIP = 'https://192.0.2.10'

headers = { 'Content-Type': 'application/json'}

# login API - you will need to login first
# and save the credentials in a cookie
loginURL = "/web/login/authenticate.do"

# cvp user and password
USER = 'arista'
PASSWORD = 'arista'

# First we have to login and save the session in a cookie
# which can be later referred to make API calls
response = requests.post(cvpIP+loginURL,json={'userId':USER,'password':PASSWORD},headers=headers,verify=False)
cookies = response.cookies



url = "/cvpservice/provisioning/getNetElementList.do"

querystring = {"nodeId":"undefined_container","startIndex":"0","endIndex":"0","ignoreAdd":"true","Accept":"application/json"}

headers = {
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.get(cvpIP+url, headers=headers, cookies=cookies, params=querystring,verify=False)
print "Response headers"
pp(response.headers)
print "-"*80
print "\n"
print "Devices in undefined container are:"
pp(response.text)
