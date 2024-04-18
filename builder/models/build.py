"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

from django.db import models

from builder.models.common import StringMap
from builder.models.common import StringList
from builder.models.secrets import UsedSecret
from builder.models.service import Service


class BuildConfiguration(models.Model):
    """
    Dictates how a Service's container should be built
    """
    service: Service = models.ForeignKey(Service, on_delete=models.CASCADE)
    context = models.FilePathField(
        default=".",
        help_text="defines either a path to a directory containing a Dockerfile, or a URL to a git repository."
    )

    dockerfile = models.CharField(
        max_length=255,
        help_text="The name of an alternate Dockerfile to use when building (like 'Dockerfile-dev' or 'Dockerfile-web')",
        blank=True,
        null=True
    )

    # dockerfile_inline is a bit too in the weeds for now, so that won't be included

    # ssh is a bit too in the weeds for now so that won't be included

    # cache_from is a bit too in the weeds for now so that won't be included

    # cache_to is a bit too in the weeds for now so that won't be included

    # additional_context is a bit too in the weeds for now so that won't be included

    # extra_hosts is a bit too in the weeds for now so that won't be included

    # isolation is a bit too in the weeds for now so that won't be included

    # priviledged is a bit too in the weeds for now so that won't be included

    # no_cache is a bit too in the weeds (though not as bad as the others) so that won't be included for now

    # pull is a bit too in the weeds for now so that won't be included

    # Network is a bit too in the weeds for now so that won't be included

    # shm_size is a bit too in the weeds for now so that won't be included

    target: str = models.CharField(
        max_length=255,
        help_text="Defines the stage to build as defined inside a multi-stage Dockerfile"
    )

    # ulimits is a bit too in the weeds for now so that won't be included

    # platforms is a bit too in the weeds for now so that won't be included

    @property
    def is_short_form(self) -> bool:
        return (
            self.dockerfile is None
            and self.target is None
            and not self.args.exists()
            and not self.labels.exists()
            and not self.secrets.exists()
            and not self.tags.exists()
        )

    @property
    def value(self) -> typing.Union[str, typing.Dict[str, typing.Any]]:
        if self.is_short_form:
            return self.context

        configuration = {
            "context": self.context
        }

        if self.dockerfile is not None:
            configuration["dockerfile"] = self.dockerfile

        if self.target is not None:
            configuration["target"] = self.target

        if self.args.exists():
            args = {}
            for arg in self.args.all():  # type: BuildArg
                args[arg.key] = arg.value
            configuration["args"] = args

        if self.labels.exists():
            labels = {}
            for label in self.labels.all():  # type: ImageLabel
                labels[label.key] = label.value
            configuration["labels"] = labels

        if self.secrets.exists():
            configuration["secrets"] = [
                secret.value
                for secret in self.secrets.all()
            ]

        if self.tags.exists():
            configuration["tags"] = [
                tag.value
                for tag in self.tags.all()
            ]
        return configuration


class BuildArg(StringMap):
    """
    Dockerfile ARG values
    """
    build_configuration = models.ForeignKey(BuildConfiguration, on_delete=models.CASCADE, related_name="args")


class ImageLabel(StringMap):
    """
    Additional metadata for a Docker image

    For example:
        build:
          context: .
          labels:
            com.example.description: "Accounting webapp"
            com.example.department: "Finance"
            com.example.label-with-empty-value: ""
    """
    build_configuration = models.ForeignKey(BuildConfiguration, on_delete=models.CASCADE, related_name="labels")


class BuildSecret(UsedSecret):
    """
    A secret used when building a Docker image
    """
    build_configuration = models.ForeignKey(BuildConfiguration, on_delete=models.CASCADE, related_name="secrets")


class ImageTags(StringList):
    """
    Tags to attach to a built image
    """
    build_configuration = models.ForeignKey(BuildConfiguration, on_delete=models.CASCADE, related_name="tags")