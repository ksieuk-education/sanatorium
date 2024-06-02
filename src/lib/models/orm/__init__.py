"""
Описание таблиц базы данных (ORM)
"""

from .base import *
from .dining import *
from .physician import *
from .registration import *
from .room import *
from .travel_package import *
from .user import *

__all__ = [
    "Admin",
    "Base",
    "DiningTable",
    "DiningType",
    "IdCreatedUpdatedBaseMixin",
    "Physician",
    "Registration",
    "Room",
    "RoomType",
    "TravelPackage",
    "User",
]
