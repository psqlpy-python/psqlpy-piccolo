import os

from piccolo.conf.apps import AppConfig

from tests.test_apps.mega.tables import MegaTable, SmallTable

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))  # noqa: PTH120, PTH100


APP_CONFIG = AppConfig(
    app_name="music",
    table_classes=[MegaTable, SmallTable],
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),  # noqa: PTH118
    commands=[],
)
