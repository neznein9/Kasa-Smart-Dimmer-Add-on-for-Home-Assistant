"""Kasa Smart Dimmer integration."""

from __future__ import annotations

# import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from kasa import Discover
from .const import DOMAIN

# _LOGGER = logging.getLogger(__name__)

SERVICE_SET_STANDBY_BRIGHTNESS = "set_standby_brightness"

ATTR_BRIGHTNESS = "brightness"
ATTR_HOST = "host"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_BRIGHTNESS): vol.All(
            vol.Coerce(int),
            vol.Range(min=0, max=100),
        ),
        vol.Optional(ATTR_HOST): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    """Set up Kasa Smart Dimmer from a config entry."""
    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: Any) -> bool:
    """Unload a config entry."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_STANDBY_BRIGHTNESS):
        hass.services.async_remove(DOMAIN, SERVICE_SET_STANDBY_BRIGHTNESS)

    return True


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Kasa Smart Dimmer integration."""
    _register_services(hass)
    return True


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SET_STANDBY_BRIGHTNESS):
        return

    async def handle_set_standby_brightness(call: ServiceCall) -> None:
        entity_id: str = call.data[ATTR_ENTITY_ID]
        brightness: int = call.data[ATTR_BRIGHTNESS]

        if not entity_id.startswith("light."):
            raise HomeAssistantError(
                f"{DOMAIN}.{SERVICE_SET_STANDBY_BRIGHTNESS} only supports light entities"
            )

        try:
            #
            # First try the modern TP-Link/Tapo path using the live device
            # already managed by Home Assistant.
            #
            entity_components = hass.data.get("entity_components", {})
            entity_component = entity_components.get("light")

            if entity_component is not None:
                entity = entity_component.get_entity(entity_id)

                if (
                    entity is not None
                    and hasattr(entity, "coordinator")
                    and hasattr(entity.coordinator, "device")
                ):
                    device = entity.coordinator.device

                    await device.update()

                    if "Brightness" in device.modules:
                        # set_brightness() turns the light on.
                        # Calling set_device_info with device_on=False updates the
                        # standby brightness while keeping the relay off.
                        await device.modules["Brightness"].call(
                            "set_device_info",
                            {
                                "brightness": brightness,
                                "device_on": False,
                            }
                        )

                        return

            #
            # Fallback for legacy KS220 dimmers.
            #
            host: str | None = call.data.get(ATTR_HOST)

            if host is None:
                host = _resolve_host_from_entity(hass, entity_id)

            if host is None:
                raise HomeAssistantError(
                    f"Could not resolve host/IP address for {entity_id}"
                )

            device = await Discover.discover_single(host)

            if device is None:
                raise HomeAssistantError(
                    f"No Kasa device discovered at {host}"
                )

            await device.update()

            response = await device.protocol.query(
                {
                    "smartlife.iot.dimmer": {
                        "set_brightness": {
                            "brightness": brightness,
                        }
                    }
                }
            )

            error_code = (
                response
                .get("smartlife.iot.dimmer", {})
                .get("set_brightness", {})
                .get("err_code")
            )

            if error_code is not None and error_code != 0:
                raise HomeAssistantError(
                    f"Kasa set_brightness failed for {entity_id}: {response}"
                )

        except HomeAssistantError:
            raise

        except Exception as err:
            raise HomeAssistantError(
                f"Failed setting standby brightness for {entity_id}: {err}"
            ) from err

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_STANDBY_BRIGHTNESS,
        handle_set_standby_brightness,
        schema=SERVICE_SCHEMA,
    )


def _resolve_host_from_entity(
    hass: HomeAssistant,
    entity_id: str,
) -> str | None:
    """Resolve host/IP address from an entity."""

    state = hass.states.get(entity_id)

    if state is not None:
        direct_host = state.attributes.get("host") or state.attributes.get("ip")

        if direct_host is not None:
            return str(direct_host)

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    entity_entry = entity_registry.async_get(entity_id)

    if entity_entry is None or entity_entry.device_id is None:
        return None

    device_entry = device_registry.async_get(entity_entry.device_id)

    if device_entry is None:
        return None

    for related_entity_entry in er.async_entries_for_device(
        entity_registry,
        device_entry.id,
    ):
        related_state = hass.states.get(related_entity_entry.entity_id)

        if related_state is None:
            continue

        if related_entity_entry.entity_id.startswith("device_tracker."):
            tracker_ip = related_state.attributes.get("ip")

            if tracker_ip is not None:
                return str(tracker_ip)

    return None
