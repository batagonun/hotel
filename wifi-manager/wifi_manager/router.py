"""Router integration point for pausing and resuming a device's connection.

The prototype ships without a real router adapter. A concrete adapter will use
the router's official API (or its documented admin interface) to add the
device's MAC address to the router's block list and remove it again.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class RouterNotConfigured(RuntimeError):
    pass


class RouterAdapter(ABC):
    name = "router"

    @abstractmethod
    def block(self, mac: str) -> None:
        """Stop the device with this MAC address from using the network."""

    @abstractmethod
    def unblock(self, mac: str) -> None:
        """Allow the device with this MAC address back onto the network."""


class PlaceholderRouter(RouterAdapter):
    """Used until a router model is chosen; every action reports it is not set up."""

    name = "غير مُعدّ"

    def block(self, mac: str) -> None:
        raise RouterNotConfigured(
            f"لم يُربط التطبيق بالراوتر بعد، لذلك لم يُوقف اتصال الجهاز {mac}."
        )

    def unblock(self, mac: str) -> None:
        raise RouterNotConfigured(
            f"لم يُربط التطبيق بالراوتر بعد، لذلك لم يُعد اتصال الجهاز {mac}."
        )
