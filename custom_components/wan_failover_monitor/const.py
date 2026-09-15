"""Constants for the WAN Failover Monitor integration."""
from __future__ import annotations

DOMAIN = "wan_failover_monitor"

CONF_TOPIC_PREFIX = "topic_prefix"
CONF_ENABLE_CELLULAR = "enable_cellular"
CONF_NAME = "name"

DEFAULT_NAME = "WAN Failover Router"

PLATFORMS = ["sensor", "binary_sensor"]

# Topic suffixes, appended to the user-configured topic prefix. Fixed by
# convention rather than individually configurable -- a publisher
# implementing this integration's contract publishes exactly these
# (see README.md for the full contract and payload formats).
TOPIC_ACTIVE_WAN = "wan_status"
TOPIC_PRIMARY_UPLINK = "interfaces/nbn"
TOPIC_CELLULAR_UPLINK = "interfaces/cellular"
TOPIC_NEXT_CHECK = "next_check"
TOPIC_CELLULAR_NETWORK_TYPE = "cellular/network_type"
TOPIC_CELLULAR_PPP_STATUS = "cellular/ppp_status"
TOPIC_CELLULAR_SIGNAL_DBM = "cellular/signal_dbm"
TOPIC_CELLULAR_SIGNALBAR = "cellular/signalbar"
TOPIC_CELLULAR_WAN_IP = "cellular/wan_ip"
TOPIC_CELLULAR_IMEI = "cellular/imei"
