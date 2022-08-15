import cvp
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

host = '192.0.2.10'


d = cvp.Cvp(host,True,443)
d.authenticate('arista','arista')
container = d.getContainer('Tommy test')
configletBuilder = d.getConfiglet("sys_telemetrybuilderv2")


# add configlet to Container, in this case adding the SYS_TelemetryBuilderV2 to 'Tommy test' container
d.mapConfigletToContainer(container,[configletBuilder])


# generate Configlets for Container based on configlet builder
d.generateConfigletForContainer(container, configletBuilder, devicesList=None, inputs=None)

# Result:
# [Configlet "SYS_TelemetryBuilderV2_192.0.2.140_1", Configlet "SYS_TelemetryBuilderV2_192.0.2.132_2"]

