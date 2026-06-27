"""
Feature 01: User access management

- Logs the sign in and sign out timestamps of a user's session.
- Users can view and search their own logs but cannot modify or delete them.
"""

from datetime import datetime, timezone
from ._base import BaseModel
from .user import User
from peewee import DateTimeField, IntegerField, ForeignKeyField
from enum import IntEnum


class AccessLogType(IntEnum):
    LOGIN = 0
    LOGOUT = 1


class AccessLog(BaseModel):
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    type = IntegerField()
    user = ForeignKeyField(User, on_delete="CASCADE", backref="access_logs")
