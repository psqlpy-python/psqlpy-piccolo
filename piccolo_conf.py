"""This piccolo_conf file is just here so migrations can be made for Piccolo's own internal apps.

For example:

python -m piccolo.main migration new user --auto

"""

import os

from piccolo.conf.apps import AppRegistry

from psqlpy_piccolo import PSQLPyEngine

DB = PSQLPyEngine(
    config={
        "host": os.environ.get("PG_HOST", "127.0.0.1"),
        "port": os.environ.get("PG_PORT", 5432),
        "user": os.environ.get("PG_USER", "postgres"),
        "password": os.environ.get("PG_PASSWORD", "postgres"),
        "database": os.environ.get("PG_DATABASE", "piccolo"),
    },
)

# from piccolo.apps.migrations.tables
APP_REGISTRY = AppRegistry(
    apps=[
        "piccolo.apps.migrations.piccolo_app",
        "tests.test_apps.mega.piccolo_app",
        "tests.test_apps.music.piccolo_app",
    ],
)
