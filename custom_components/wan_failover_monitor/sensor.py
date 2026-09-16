"""Sensor entities for WAN Failover Monitor."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENABLE_CELLULAR,
    TOPIC_ACTIVE_WAN,
    TOPIC_CELLULAR_DATA_ALLOTTED,
    TOPIC_CELLULAR_DATA_PLANTYPE,
    TOPIC_CELLULAR_DATA_REMAINING,
    TOPIC_CELLULAR_DATA_REMAINING_DAYS,
    TOPIC_CELLULAR_DATA_REMAINING_PERCENT,
    TOPIC_CELLULAR_DATA_USED,
    TOPIC_CELLULAR_IMEI,
    TOPIC_CELLULAR_NETWORK_TYPE,
    TOPIC_CELLULAR_PPP_STATUS,
    TOPIC_CELLULAR_SIGNALBAR,
    TOPIC_CELLULAR_SIGNAL_DBM,
    TOPIC_CELLULAR_WAN_IP,
    TOPIC_NEXT_CHECK,
)
from .entity import WanFailoverMqttEntity


@dataclass(frozen=True, kw_only=True)
class WanFailoverSensorDescription(SensorEntityDescription):
    """Describes one MQTT-backed sensor."""

    topic_suffix: str = ""
    cellular: bool = False


SENSOR_DESCRIPTIONS: tuple[WanFailoverSensorDescription, ...] = (
    WanFailoverSensorDescription(
        key="active_wan",
        name="Active WAN",
        icon="mdi:swap-horizontal",
        topic_suffix=TOPIC_ACTIVE_WAN,
    ),
    WanFailoverSensorDescription(
        key="next_check",
        name="Next Check",
        device_class=SensorDeviceClass.TIMESTAMP,
        topic_suffix=TOPIC_NEXT_CHECK,
    ),
    WanFailoverSensorDescription(
        key="cellular_network_type",
        name="Cellular Network Type",
        icon="mdi:signal",
        topic_suffix=TOPIC_CELLULAR_NETWORK_TYPE,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_signal",
        name="Cellular Signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dBm",
        topic_suffix=TOPIC_CELLULAR_SIGNAL_DBM,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_signal_bars",
        name="Cellular Signal Bars",
        icon="mdi:signal-cellular-3",
        state_class=SensorStateClass.MEASUREMENT,
        topic_suffix=TOPIC_CELLULAR_SIGNALBAR,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_ppp_status",
        name="Cellular PPP Status",
        icon="mdi:signal-variant",
        topic_suffix=TOPIC_CELLULAR_PPP_STATUS,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_wan_ip",
        name="Cellular WAN IP",
        icon="mdi:ip-network",
        topic_suffix=TOPIC_CELLULAR_WAN_IP,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_imei",
        name="Cellular IMEI",
        entity_category=EntityCategory.DIAGNOSTIC,
        topic_suffix=TOPIC_CELLULAR_IMEI,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_plantype",
        name="Cellular Data Plan Type",
        icon="mdi:sim",
        entity_category=EntityCategory.DIAGNOSTIC,
        topic_suffix=TOPIC_CELLULAR_DATA_PLANTYPE,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_allotted",
        name="Cellular Data Allotted",
        icon="mdi:database",
        state_class=SensorStateClass.MEASUREMENT,
        topic_suffix=TOPIC_CELLULAR_DATA_ALLOTTED,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_used",
        name="Cellular Data Used",
        icon="mdi:database-arrow-up",
        state_class=SensorStateClass.MEASUREMENT,
        topic_suffix=TOPIC_CELLULAR_DATA_USED,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_remaining",
        name="Cellular Data Remaining",
        icon="mdi:database-arrow-down",
        state_class=SensorStateClass.MEASUREMENT,
        topic_suffix=TOPIC_CELLULAR_DATA_REMAINING,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_remaining_days",
        name="Cellular Data Remaining Days",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="d",
        topic_suffix=TOPIC_CELLULAR_DATA_REMAINING_DAYS,
        cellular=True,
    ),
    WanFailoverSensorDescription(
        key="cellular_data_remaining_percent",
        name="Cellular Data Remaining Percent",
        icon="mdi:database-clock",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        topic_suffix=TOPIC_CELLULAR_DATA_REMAINING_PERCENT,
        cellular=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for a config entry."""
    enable_cellular = entry.options.get(
        CONF_ENABLE_CELLULAR, entry.data.get(CONF_ENABLE_CELLULAR, True)
    )
    async_add_entities(
        WanFailoverSensor(hass, entry, description)
        for description in SENSOR_DESCRIPTIONS
        if enable_cellular or not description.cellular
    )


class WanFailoverSensor(WanFailoverMqttEntity, SensorEntity):
    """A sensor fed by a single MQTT topic."""

    entity_description: WanFailoverSensorDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: WanFailoverSensorDescription,
    ) -> None:
        super().__init__(hass, entry, description.topic_suffix, description.key)
        self.entity_description = description

    def _handle_payload(self, payload: str) -> None:
        payload = payload.strip()
        if not payload:
            self._attr_native_value = None
            return

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            # Publishers are expected to send ISO 8601 (Z or +00:00 offset).
            self._attr_native_value = dt_util.parse_datetime(payload)
            return

        if self.entity_description.state_class is not None:
            # Any sensor with a state_class is numeric -- cast for graphing.
            try:
                value = float(payload)
            except ValueError:
                self._attr_native_value = None
            else:
                self._attr_native_value = int(value) if value.is_integer() else value
            return

        self._attr_native_value = payload
