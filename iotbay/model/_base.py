from peewee import AutoField, Model

from ..db import db


class BaseModel(Model):
    id = AutoField()

    class Meta:
        database = db
