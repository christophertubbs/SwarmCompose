"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

from django.db import models
from django.core.validators import RegexValidator

IP_RANGE_VALIDATOR = RegexValidator(
    r'^(\d{3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,2})\/\d{2}$',
    message='Values must be in the format of "10.226.126.0/24" or "192.168.127.12/27"'
)


class Network(models.Model):
    """
    Defines how a network may be created and referenced
    """
    name: str = models.CharField(max_length=255, help_text="The name of the network that services will reference")
    driver: str = models.CharField(
        max_length=255,
        help_text="Which driver should be used for this network",
        blank=True,
        null=True
    )
    attachable: bool = models.BooleanField(
        default=False,
        help_text="If attachable is set to true, then standalone containers should be able to attach to this network, "
                  "in addition to services. If a standalone container attaches to the network, it can communicate with "
                  "services and other standalone containers that are also attached to the network. Swarm services will "
                  "be able to communicate either way"
    )
    external: bool = models.BooleanField(
        default=False,
        help_text="Specifies that this network’s lifecycle is maintained outside of that of the application. "
                  "Compose doesn't attempt to create these networks, and returns an error if one doesn't exist. "
                  "All other attributes apart from name are irrelevant. If Compose detects any other attribute, "
                  "it rejects the Compose file as invalid."
    )
    internal: bool = models.BooleanField(
        default=False,
        help_text="By default, Compose provides external connectivity to networks. internal, when set to true, allows "
                  "you to create an externally isolated network."
    )

    @classmethod
    def get_stock_drivers(cls) -> typing.List[typing.Tuple[str, str, str]]:
        """
        Get a list of tuples that may populate drop downs with options for network drivers

        [0]: The value for a drop down menu
        [1]: The text for a drop down menu
        [2]: A description of what the value means

        :return: The list of tuples that may populate drop downs
        """
        return [
            (
                "bridge",
                "Bridge",
                "Bridge networks are commonly used when your application runs in a container that needs to "
                "communicate with other containers on the same host."
            ),
            (
                "host",
                "Host",
                "Remove network isolation between the container and the Docker host, and use the host's "
                "networking directly"
            ),
            (
                "overlay",
                "Overlay",
                "Overlay networks connect multiple Docker daemons together and enable Swarm services and containers to "
                "communicate across nodes. This strategy removes the need to do OS-level routing."
            ),
            (
                "ipvlan",
                "IPvlan",
                "IPvlan networks give users total control over both IPv4 and IPv6 addressing. The VLAN driver builds "
                "on top of that in giving operators complete control of layer 2 VLAN tagging and even IPvlan L3 "
                "routing for users interested in underlay network integration."
            ),
            (
                "macvlan",
                "Macvlan",
                "Macvlan networks allow you to assign a MAC address to a container, making it appear as a physical "
                "device on your network. The Docker daemon routes traffic to containers by their MAC addresses. "
                "Using the macvlan driver is sometimes the best choice when dealing with legacy applications that "
                "expect to be directly connected to the physical network, rather than routed through the Docker host's "
                "network stack."
            )
        ]

    @property
    def value(self) -> typing.Dict[str, typing.Any]:
        config = {
            "name": self.name
        }

        if self.attachable:
            config["attachable"] = self.attachable

        if self.internal:
            config["internal"] = self.internal

        if self.external:
            config["external"] = self.external

        if self.driver:
            config["driver"] = self.driver

        if self.labels.exists():
            config["labels"] = {
                option.key: option.label
                for option in self.labels.all()
            }

        if self.driver_opts.exists():
            config["driver_opts"] = {
                option.key: option.value
                for option in self.driver_opts.all()
            }

        if self.ipam_configs.exists():
            configurations = [
                config.value
                for config in self.ipam_configs.all()
                if config.is_populated
            ]

            if configurations:
                config['ipam'] = {
                    "driver": "default",
                    "config": configurations
                }

        return config


class NetworkDriverOptions(models.Model):
    """
    Additional options for chosen network drivers
    """
    network: Network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="driver_opts")
    key: str = models.CharField(max_length=255, help_text="The name of the option")
    value: str = models.CharField(max_length=255, help_text="The value for the option")


class NetworkLabel(models.Model):
    """
    Metadata that may be attached to networks as a series of names
    """
    network: Network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="labels")
    key: str = models.CharField(
        max_length=255,
        help_text="The metadata key to attach the label to. It is recommended that you use reverse-DNS notation to "
                  "prevent labels from conflicting with those used by other software."
    )
    label: str = models.CharField(max_length=255, help_text="The text for the label")


class IPAddressManagementConfig(models.Model):
    """
    Represents the IPAM configuration for Networks

    Configs are generally stored as many configs on a central IPAM object, but IPAM drivers and IPAM driver options
    aren't going to be supported, so this links directly back at the network
    """
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="ipam_configs")
    driver = models.CharField(max_length=255, help_text="The type of driver to use", blank=True, null=True)
    subnet = models.CharField(max_length=255, help_text="", blank=True, null=True, validators=[IP_RANGE_VALIDATOR])
    ip_range = models.CharField(max_length=255, help_text="", blank=True, null=True, validators=[IP_RANGE_VALIDATOR])
    gateway = models.GenericIPAddressField(
        help_text="The address of the gateway that this configuration should use",
        blank=True,
        null=True
    )

    @property
    def is_populated(self) -> bool:
        """
        Whether any values were set for this IPAM were configured
        """
        return (
                self.driver is not None
                or self.subnet is not None
                or self.ip_range is not None
                or self.gateway is not None
        )

    @property
    def value(self) -> typing.Dict[str, typing.Any]:
        configuration: typing.Dict[str, typing.Any] = {}

        if self.driver is not None:
            configuration["driver"] = self.driver

        if self.subnet is not None:
            configuration["subnet"] = self.subnet

        if self.ip_range is not None:
            configuration["ip_range"] = self.ip_range

        if self.gateway is not None:
            configuration["gateway"] = self.gateway

        if self.auxilary_addresses.exist():
            configuration["aux_addresses"] = {
                auxilary_address.address_name: auxilary_address.address
                for auxilary_address in self.auxilary_addresses.all()
            }

        return configuration


class IPAMAuxilaryAddresses(models.Model):
    """
    Auxiliary IPv4 or IPv6 address used by a Network driver, as a mapping from hostname to IP
    """
    ipam = models.ForeignKey(IPAddressManagementConfig, on_delete=models.CASCADE, related_name="auxilary_addresses")
    address_name = models.CharField(max_length=255, help_text="An identifiable name for the address")
    address = models.GenericIPAddressField(
        help_text="The IP address"
    )