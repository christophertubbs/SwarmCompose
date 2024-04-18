"""
@TODO: Put a module wide description here
"""

from django.db import models


class StringList(models.Model):
    """
    An abstract model that specifies a list of values that can be used as a field for another model.

    Subclasses should only need to add a field for the foreign key
    """
    class Meta:
        abstract = True

    value: str = models.CharField(max_length=255)


class StringMap(models.Model):
    """
    An abstract model that maps a key string to a value string that can be used as a field for another model.

    Subclasses should only need to add a field for the foreign key
    """
    class Meta:
        abstract = True

    key: str = models.CharField(max_length=255)
    value: str = models.CharField(max_length=255)
