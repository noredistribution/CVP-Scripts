# SYS_TelemetryBuilderV2_Prometheus

This builder was written to generate the possible combinations for TerminAttr and ocPrometheus daemon
configurations based on https://eos.arista.com/streaming-eos-telemetry-states-to-prometheus/

![alt text](https://github.com/noredistribution/CVP-Scripts/blob/master/configlet_builders/ocprometheusbuilder.png)

# SYS_TelemetryBuilderV2_loopback

Using this builder you can set the `-cvsourceip` in TerminAttr based on the input Source Interface.
The builder queries the switch what primary IP has under the interface specified and will use that as a source for streaming.

![alt text](https://github.com/noredistribution/CVP-Scripts/blob/master/configlet_builders/terminattrwithloopback.png)
