from typing import TypeVar

from baton.models import Collection, DataObject

# Type of iRODS entity
EntityType = TypeVar('T', DataObject, Collection)

# Object type returned by the custom object mapper
CustomObjectType = TypeVar('V')