# **Test AAA Server connectivity from CVP**

Install pip requirements from requirements.txt
```pip install -r requirements.txt```


### **TACACS example:**

```python  testaaa.py --host 192.0.2.2 --user=cvpuser --password=cvppassword --aaaip=192.0.2.200 --aaasecret=arista --authmode=ASCII --aaaport=49 --aaatype=TACACS --aaauser=tacacsuser --aaapassword=tacacspassword --aaaaccountport=0```


### **RADIUS example:**

```python  testaaa.py --host 192.0.2.2 --user=cvpuser --password=cvppassword --aaaip=192.0.2.200 --aaasecret=arista --authmode=PAP --aaaport=1812 --aaatype=RADIUS --aaauser=radiususer --aaapassword=radiuspassword --aaaaccountport=1813```
