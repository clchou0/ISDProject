import os
from pathlib import Path
import secrets
import subprocess

from .routes import register_blueprints
from . import app, is_production
from .db import db, init_db
from .model import ALL_MODELS

init_db()
db.create_tables(ALL_MODELS)

register_blueprints()


def create_secret_key_if_not_exists():
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text(f"SECRET_KEY={secrets.token_hex()}\n")
        print("generated secret key")


def dev():
    app.run("127.0.0.1", port=5001, debug=True)


def prod():
    os.environ["FLASK_ENV"] = "production"
    create_secret_key_if_not_exists()
    subprocess.run(["gunicorn", "iotbay.__main__:app"], check=True)


if __name__ == "__main__":
    if is_production:
        prod()
    else:
        dev()
