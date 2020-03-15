## Webhook relay for sending event alerts from CVP to Google Hangouts Chat

### Usage

Run this script on any server that can communicate with CVP and has internet access to forward the events to Google Chat

```

python cvp_ghc_alert --ghcURL <GHC webhook URL>

```

On CVP go to the **Events** page --> Configure Notifications/Event Alerts --> Receivers and add a new receiver with a Webhook configuration and point it to your apps URL: http://x.x.x.x:5001/webhook

### Example card

![Alt text](https://github.com/noredistribution/CVP-Scripts/blob/master/cvp_ghc_alerter/cvpghcalertcard.png?raw=true)

### Run it as docker container

1\. Build the image from the Dockerfile

`dockebuild -f Dockerfile -t ghcalerter:latest .`

2\. Run container with the webhook URL as an argument

`docker run  -p 5001:5001 ghcalerter '<COPY WEBHOOK URL HERE>'`
