"""Kasa Smart Dimmer integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_SET_STANDBY_BRIGHTNESS = "set_standby_brightness"

ATTR_BRIGHTNESS = "brightness"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_BRIGHTNESS): vol.All(
            vol.Coerce(int),
            vol.Range(min=0, max=100),
        ),
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: Any,
) -> bool:
    """Set up Kasa Smart Dimmer from a config entry."""
    _register_services(hass)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: Any,
) -> bool:
    """Unload a config entry."""

    if hass.services.has_service(
        DOMAIN,
        SERVICE_SET_STANDBY_BRIGHTNESS,
    ):
        hass.services.async_remove(
            DOMAIN,
            SERVICE_SET_STANDBY_BRIGHTNESS,
        )

    return True


async def async_setup(
    hass: HomeAssistant,
    config: dict[str, Any],
) -> bool:
    """Set up the Kasa Smart Dimmer integration."""
    _register_services(hass)
    return True


def _register_services(
    hass: HomeAssistant,
) -> None:
    if hass.services.has_service(
        DOMAIN,
        SERVICE_SET_STANDBY_BRIGHTNESS,
    ):
        return

    async def handle_set_standby_brightness(
        call: ServiceCall,
    ) -> None:
        entity_id: str = call.data[ATTR_ENTITY_ID]
        brightness: int = call.data[ATTR_BRIGHTNESS]

        if not entity_id.startswith("light."):
            raise HomeAssistantError(
                f"{DOMAIN}.{SERVICE_SET_STANDBY_BRIGHTNESS} only supports light entities"
            )

        try:
            entity_components = hass.data.get(
                "entity_components",
                {},
            )

            entity_component = entity_components.get("light")

            if entity_component is None:
                raise HomeAssistantError(
                    "Light entity component not found"
                )

            entity = entity_component.get_entity(entity_id)

            if entity is None:
                raise HomeAssistantError(
                    f"Entity not found: {entity_id}"
                )

            if (
                not hasattr(entity, "coordinator")
                or not hasattr(entity.coordinator, "device")
            ):
                raise HomeAssistantError(
                    f"{entity_id} is not a supported TP-Link dimmer"
                )

            device = entity.coordinator.device

            await device.update()

            #
            # Newer Tapo dimmers (S515D, etc.)
            #
            if "Brightness" in device.modules:
                is_on = device.is_on
                # set_brightness() turns the light on.
                # Calling set_device_info with device_on=False updates
                # the standby brightness while keeping the relay off.
                await device.modules["Brightness"].call(
                    "set_device_info",
                    {
                        "brightness": brightness,
                        "device_on": is_on,
                    },
                )

                return

            #
            # Legacy Kasa dimmers (KS220)
            #
            if "dimmer" in device.modules:
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

                if (
                    error_code is not None
                    and error_code != 0
                ):
                    raise HomeAssistantError(
                        f"Kasa set_brightness failed: {response}"
                    )

                return

            raise HomeAssistantError(
                f"Unsupported TP-Link dimmer type: {type(device)}"
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
