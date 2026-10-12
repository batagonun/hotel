"""Router integration point for pausing and resuming a device's connection.

Only routers with an official API get a blocking adapter. The user's router
(Soyealink B311-922, supplied by Vodafone) has no published API, so the app
runs view-only and sends the user to the router's own admin page to block a
device there.
"""

from __future__ import annotations

import webbrowser
from abc import ABC, abstractmethod


class RouterAdapter(ABC):
    name = "router"
    supports_blocking = False

    @abstractmethod
    def block(self, mac: str) -> None:
        """Stop the device with this MAC address from using the network."""

    @abstractmethod
    def unblock(self, mac: str) -> None:
        """Allow the device with this MAC address back onto the network."""


class ViewOnlyRouter(RouterAdapter):
    """A router without an official API: blocking happens in its own admin page."""

    supports_blocking = False

    def __init__(self, name: str, admin_url: str) -> None:
        self.name = name
        self.admin_url = admin_url

    def open_admin_page(self) -> None:
        webbrowser.open(self.admin_url)

    def block(self, mac: str) -> None:
        raise NotImplementedError("هذا الراوتر لا يوفّر واجهة رسمية للحظر.")

    unblock = block


def default_router() -> ViewOnlyRouter:
    return ViewOnlyRouter("Soyealink B311-922 (عرض فقط)", "http://192.168.8.1/")
