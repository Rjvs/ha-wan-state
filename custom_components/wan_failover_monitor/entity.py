"""Shared MQTT-backed entity base for WAN Failover Monitor."""
from __future__ import annotations

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import CONF_NAME, CONF_TOPIC_PREFIX, DEFAULT_NAME, DOMAIN


class WanFailoverMqttEntity(Entity):
    """Base entity that subscribes to a single MQTT state topic.

    Push-based (local_push), not polled: state only changes when the
    publisher sends a new MQTT message, so there's no coordinator here --
    each entity manages its own subscription directly.
    """

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        topic_suffix: str,
        unique_id_suffix: str,
    ) -> None:
        self.hass = hass
        self._entry = entry
        prefix = entry.data[CONF_TOPIC_PREFIX]
        self._topic = f"{prefix}/{topic_suffix}"
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="DIY",
            model="WAN failover router",
        )
        self._unsubscribe = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to this entity's MQTT topic once added to hass."""

        @callback
        def _message_received(msg: mqtt.ReceiveMessage) -> None:
            self._handle_payload(msg.payload)
            self.async_write_ha_state()

        self._unsubscribe = await mqtt.async_subscribe(
            self.hass, self._topic, _message_received, qos=0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe when the entity is removed."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    def _handle_payload(self, payload: str) -> None:
        """Interpret a raw MQTT payload. Overridden by subclasses."""
        raise NotImplementedError
