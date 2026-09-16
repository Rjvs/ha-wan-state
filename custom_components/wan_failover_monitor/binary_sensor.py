"""Binary sensor entities for WAN Failover Monitor."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ENABLE_CELLULAR,
    TOPIC_CELLULAR_DATA_LOWBALANCE,
    TOPIC_CELLULAR_UPLINK,
    TOPIC_PRIMARY_UPLINK,
)
from .entity import WanFailoverMqttEntity


@dataclass(frozen=True, kw_only=True)
class WanFailoverBinarySensorDescription(BinarySensorEntityDescription):
    """Describes one MQTT-backed binary sensor."""

    topic_suffix: str = ""
    cellular: bool = False


BINARY_SENSOR_DESCRIPTIONS: tuple[WanFailoverBinarySensorDescription, ...] = (
    WanFailoverBinarySensorDescription(
        key="primary_uplink",
        name="Primary Uplink",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        topic_suffix=TOPIC_PRIMARY_UPLINK,
    ),
    WanFailoverBinarySensorDescription(
        key="cellular_uplink",
        name="Cellular Uplink",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        topic_suffix=TOPIC_CELLULAR_UPLINK,
    ),
    WanFailoverBinarySensorDescription(
        key="cellular_data_lowbalance",
        name="Cellular Data Low Balance",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        topic_suffix=TOPIC_CELLULAR_DATA_LOWBALANCE,
        cellular=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensors for a config entry."""
    enable_cellular = entry.options.get(
        CONF_ENABLE_CELLULAR, entry.data.get(CONF_ENABLE_CELLULAR, True)
    )
    async_add_entities(
        WanFailoverBinarySensor(hass, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
        if enable_cellular or not description.cellular
    )


class WanFailoverBinarySensor(WanFailoverMqttEntity, BinarySensorEntity):
    """A binary sensor fed by a single MQTT topic (ON/OFF payloads)."""

    entity_description: WanFailoverBinarySensorDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: WanFailoverBinarySensorDescription,
    ) -> None:
        super().__init__(hass, entry, description.topic_suffix, description.key)
        self.entity_description = description

    def _handle_payload(self, payload: str) -> None:
        payload = payload.strip().upper()
        if payload == "ON":
            self._attr_is_on = True
        elif payload == "OFF":
            self._attr_is_on = False
        else:
            self._attr_is_on = None
