"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

from django.db import models

from .common import StringMap


ENDPOINT_MODE_CHOICES: typing.Iterable[typing.Tuple[str, str]] = [
    ("vip", "Assign Virtual IP"),
    ("dnsrr", "DNS Round-Robin")
]


class Deploy(models.Model):
    """
    The Compose Deploy Specification lets you declare additional metadata on services so Compose gets relevant data
    to allocate adequate resources on the platform and configure them to match your needs.
    """
    endpoint_mode: typing.Optional[str] = models.CharField(
        max_length=10,
        choices=ENDPOINT_MODE_CHOICES,
        blank=True,
        null=True,
        help_text="Specifies a service discovery method for external clients connecting to a service"
    )


class DeployLabel(StringMap):
    """
    Specifies metadata for the service. These labels are only set on the service and not the containers
    """
    deploy: Deploy = models.ForeignKey(Deploy, on_delete=models.CASCADE, related_name="labels")