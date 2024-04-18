"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

from django.db import models
from django.core.validators import RegexValidator

INTEGER_STRING = RegexValidator(r"^\d+$", message="The value must be at least one integer and only integers")
OCTAL_STRING = RegexValidator(r"^[0-7]{3}$", message="The value must be a 4 character octal")


class UsedSecret(models.Model):
    """
    Represents the usage of a secret
    """
    class Meta:
        abstract = True

    source: str = models.CharField(max_length=255, help_text="The name of the secret to use")
    target: str = models.CharField(
        max_length=255,
        help_text="The name of file to be mounted in '/run/secrets/' in the service's task containers. Defaults to the source value if not specified",
        null=True,
        blank=True
    )
    uid: str = models.CharField(
        max_length=255,
        help_text="The numeric UID that owns the file within /run/secrets/ in the service's task containers. "
                  "Default value is the USER running the container",
        null=True,
        blank=True,
        validators=[INTEGER_STRING]
    )
    gid: str = models.CharField(
        max_length=255,
        help_text="The numeric GID that owns the file within /run/secrets/ in the service's task containers. "
                  "Default value is the USER running the container",
        null=True,
        blank=True,
        validators=[INTEGER_STRING]
    )
    mode: str = models.CharField(
        max_length=4,
        help_text="he permissions for the file to be mounted in /run/secrets/ in the service's task containers, "
                  "in octal notation. Default value is world-readable permissions (mode 0444). The writable bit must "
                  "be ignored if set. The executable bit may be set.",
        null=True,
        blank=True,
        validators=[OCTAL_STRING]
    )

    @property
    def value(self) -> typing.Union[str, typing.Dict[str, str]]:
        is_short = all(
            value is None
            for value in [self.target, self.uid, self.gid, self.mode]
        )

        if is_short:
            return self.source

        secret = {
            "source": self.source
        }

        if self.target is not None:
            secret["target"] = self.target

        if self.uid is not None:
            secret["uid"] = self.uid

        if self.gid is not None:
            secret["gid"] = self.gid

        if self.mode is not None:
            secret["mode"] = self.mode

        return secret