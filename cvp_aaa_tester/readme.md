###3Test AAA Server connectivity from CVP

Install pip requirements from requirements.txt
```pip install -r requirements.txt```


##TACACS example:

```python  testaaa.py --host 10.83.13.79 --user=cvpadmin --password=arastra --aaaip=10.83.12.221 --aaasecret=arista --authmode=ASCII --aaaport=49 --aaatype=TACACS --aaauser=tamas --aaapassword=arastra --aaaaccountport=0```


##RADIUS example:

```python  testaaa.py --host 10.83.13.79 --user=cvpadmin --password=arastra --aaaip=10.83.12.24 --aaasecret=arastra --authmode=PAP --aaaport=1812 --aaatype=RADIUS --aaauser=spiderman --aaapassword=arista1234 --aaaaccountport=1813```
