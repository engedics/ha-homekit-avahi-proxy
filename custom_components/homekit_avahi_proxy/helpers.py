"""Helpers to deal with HomeKit Bridges."""
from typing import ClassVar

from homeassistant.components import zeroconf


class HomeKitBridgeZeroconf:
    """Class to hold a zeroconf instance."""

    __zconf: ClassVar[zeroconf.HaZeroconf | None] = None

    @classmethod
    def set_zeroconf(cls, zconf: zeroconf.HaZeroconf) -> None:
        """Set zeroconf."""
        cls.__zconf = zconf

    @classmethod
    def get_zeroconf(cls) -> zeroconf.HaZeroconf | None:
        """Get zeroconf."""
        return cls.__zconf
