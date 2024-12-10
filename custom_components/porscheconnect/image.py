"""Demo image platform."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.image import Image, ImageEntity, ImageEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
    PorscheVehicle,
)
from .const import DOMAIN

CONTENT_TYPE = "image/png"


@dataclass(frozen=True)
class PorscheImageEntityDescription(ImageEntityDescription):
    """Describes a Porsche image entity."""

    view: str = None


IMAGE_TYPES: list[PorscheImageEntityDescription] = [
    PorscheImageEntityDescription(
        name="Front view",
        key="front_view",
        translation_key="front_view",
        view="frontView",
    ),
    PorscheImageEntityDescription(
        name="Side view",
        key="side_view",
        translation_key="side_view",
        view="sideView",
    ),
    PorscheImageEntityDescription(
        name="Rear view",
        key="rear_view",
        translation_key="rear_view",
        view="rearView",
    ),
    PorscheImageEntityDescription(
        name="Rear top view",
        key="rear_top_view",
        translation_key="rear_top_view",
        view="rearTopView",
    ),
    PorscheImageEntityDescription(
        name="Top view",
        key="top_view",
        translation_key="top_view",
        view="topView",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche Connect image entity from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        PorscheImage(hass, coordinator, vehicle, description)
        for vehicle in coordinator.vehicles
        for description in IMAGE_TYPES
    ]

    async_add_entities(entities)


class PorscheImage(PorscheBaseEntity, ImageEntity):
    """Representation of an image entity."""

    entity_description: PorscheImageEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheImageEntityDescription,
    ) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator, vehicle)
        ImageEntity.__init__(self, hass)

        self.entity_description = description

        self._attr_content_type = CONTENT_TYPE
        self._attr_unique_id = f'{vehicle.data["name"]}-{description.key}'
        self._attr_image_url = vehicle.picture_locations[description.view]

    async def async_added_to_hass(self):
        """Set the update time."""
        self._attr_image_last_updated = dt_util.utcnow()

    async def _async_load_image_from_url(self, url: str) -> Image | None:
        """Load an image by url."""
        if response := await self._fetch_url(url):
            image_data = response.content
            return Image(
                content=image_data,
                content_type=CONTENT_TYPE,
            )
        return None
