## Usage
`python3 aeris_rest_cc_example.py -c 10.83.12.79 -u {username} -p {password}`

## Example
```
python3 aeris_rest_cc_example.py -c 10.83.12.79 -u cvpadmin -p arastra                               15:18:26 
getCvpInfo:
calling url:  https://10.83.12.79:443/web/cvpInfo/getCvpInfo.do
{
  "version": "2019.1.3"
}
+ ------------------------------------------------------------------------------ +
Choose an action from below:


1) Get Pending Change Controls
2) Get Completed Change Controls
3) Get full list of Change Controls
4) Get the status of a Change Control
+ ------------------------------------------------------------------------------ +


Enter action:1
Get Pending CCs:
calling url:  https://10.83.12.79/api/v1/rest/cvp/changecontrol/pending
{
  "notifications": [
    {
      "timestamp": "1581426165020845840",
      "path_elements": [
        "changecontrol",
        "pending"
      ],
      "updates": {
        "656f730a-R1KR4twJg": {
          "key": "656f730a-R1KR4twJg",
          "value": {}
        }
      }
    }
  ]
}
invalid action: 1
+ ------------------------------------------------------------------------------ +
Choose an action from below:


1) Get Pending Change Controls
2) Get Completed Change Controls
3) Get full list of Change Controls
4) Get the status of a Change Control
+ ------------------------------------------------------------------------------ +


Enter action:3
Get CC list:
calling url:  https://10.83.12.79/api/v1/rest/cvp/changecontrol/status
{
  "notifications": [
    {
      "timestamp": "1575652390856135147",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-Vu0L6eUPD": {
          "key": "656f730a-Vu0L6eUPD",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-Vu0L6eUPD"
            ]
          }
        }
      }
    },
    {
      "timestamp": "1581182659040945839",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-L2txkIMP.": {
          "key": "656f730a-L2txkIMP.",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-L2txkIMP."
            ]
          }
        }
      }
    },
    {
      "timestamp": "1581185841358884464",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-QhS4zHEfT": {
          "key": "656f730a-QhS4zHEfT",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-QhS4zHEfT"
            ]
          }
        }
      }
    },
    {
      "timestamp": "1581185917273856418",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-hrCzCU5Wx": {
          "key": "656f730a-hrCzCU5Wx",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-hrCzCU5Wx"
            ]
          }
        }
      }
    }
  ]
}
+ ------------------------------------------------------------------------------ +
Choose an action from below:


1) Get Pending Change Controls
2) Get Completed Change Controls
3) Get full list of Change Controls
4) Get the status of a Change Control
+ ------------------------------------------------------------------------------ +


Enter action:4
Enter CC ID:656f730a-hrCzCU5Wx
calling url:  https://10.83.12.79/api/v1/rest/cvp/changecontrol/status/656f730a-hrCzCU5Wx/all
{
  "notifications": [
    {
      "timestamp": "1581186730534466227",
      "path_elements": [
        "changecontrol",
        "status",
        "656f730a-hrCzCU5Wx",
        "all"
      ],
      "updates": {
        "all": {
          "key": "all",
          "value": {
            "Err": "",
            "State": "Completed"
          }
        }
      }
    }
  ]
}
+ ------------------------------------------------------------------------------ +
Choose an action from below:


1) Get Pending Change Controls
2) Get Completed Change Controls
3) Get full list of Change Controls
4) Get the status of a Change Control
+ ------------------------------------------------------------------------------ +


Enter action:3
Get CC list:
calling url:  https://10.83.12.79/api/v1/rest/cvp/changecontrol/status
{
  "notifications": [
    {
      "timestamp": "1575652390856135147",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-Vu0L6eUPD": {
          "key": "656f730a-Vu0L6eUPD",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-Vu0L6eUPD"
            ]
          }
        }
      }
    },

    {
      "timestamp": "1575652390856140873",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-VcjOVLeS8": {
          "key": "656f730a-VcjOVLeS8",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-VcjOVLeS8"
            ]
          }
        }
      }
    },
    {
      "timestamp": "1581185917273856418",
      "path_elements": [
        "changecontrol",
        "status"
      ],
      "updates": {
        "656f730a-hrCzCU5Wx": {
          "key": "656f730a-hrCzCU5Wx",
          "value": {
            "ptr": [
              "changecontrol",
              "status",
              "656f730a-hrCzCU5Wx"
            ]
          }
        }
      }
    }
  ]
}
+ ------------------------------------------------------------------------------ +
Choose an action from below:


1) Get Pending Change Controls
2) Get Completed Change Controls
3) Get full list of Change Controls
4) Get the status of a Change Control
+ ------------------------------------------------------------------------------ +


Enter action:^Cexiting..
```