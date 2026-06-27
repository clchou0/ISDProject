import os

from peewee import SqliteDatabase

from . import RUNTIME_DIR


def resolve_db_name():
    is_prod = os.environ.get("FLASK_ENV") == "production"
    return "app.db" if is_prod else "app.dev.db"


db = SqliteDatabase(None)


def init_db():
    # Setting `foreign_keys` to 1 allows functionality for ON DELETE and ON CASCADE rules.
    # This means deleting a user will delete all their payment methods, since a payment
    # method stores a foreign key of a user.
    db.init(RUNTIME_DIR / resolve_db_name(), pragmas={"foreign_keys": 1})
