import os
from pathlib import Path
from typing import Protocol, cast

import flask as flask
from dotenv import load_dotenv
from peewee import SqliteDatabase

load_dotenv()

RUNTIME_DIR = Path(__file__).resolve().parent

app = flask.Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "blahblahblah")
is_production = os.environ.get("FLASK_ENV") == "production"


class FlaskGlobal(Protocol):
    db: SqliteDatabase


# Request-local flask variables. This asserts that `db` is a valid attribute of `g`.
g = cast(FlaskGlobal, cast(object, flask.g))
