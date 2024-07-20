import decimal

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete, OnUpdate
from piccolo.columns.column_types import (
    JSON,
    JSONB,
    UUID,
    BigInt,
    Boolean,
    Bytea,
    Date,
    DoublePrecision,
    ForeignKey,
    Integer,
    Interval,
    Numeric,
    Real,
    Serial,
    SmallInt,
    Text,
    Timestamp,
    Timestamptz,
    Varchar,
)
from piccolo.columns.defaults.date import DateNow
from piccolo.columns.defaults.interval import IntervalCustom
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.defaults.uuid import UUID4
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class SmallTable(Table, tablename="small_table", schema=None):  # type: ignore[call-arg]
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


ID = "2024-07-20T20:40:36:665178"
VERSION = "1.12.0"
DESCRIPTION = ""


async def forwards() -> None:
    manager = MigrationManager(
        migration_id=ID,
        app_name="mega",
        description=DESCRIPTION,
    )

    manager.add_table(
        class_name="SmallTable",
        tablename="small_table",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="MegaTable",
        tablename="mega_table",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="SmallTable",
        tablename="small_table",
        column_name="varchar_col",
        db_column_name="varchar_col",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="bigint_col",
        db_column_name="bigint_col",
        column_class_name="BigInt",
        column_class=BigInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="boolean_col",
        db_column_name="boolean_col",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="bytea_col",
        db_column_name="bytea_col",
        column_class_name="Bytea",
        column_class=Bytea,
        params={
            "default": b"",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="date_col",
        db_column_name="date_col",
        column_class_name="Date",
        column_class=Date,
        params={
            "default": DateNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="foreignkey_col",
        db_column_name="foreignkey_col",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": SmallTable,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="integer_col",
        db_column_name="integer_col",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="interval_col",
        db_column_name="interval_col",
        column_class_name="Interval",
        column_class=Interval,
        params={
            "default": IntervalCustom(
                weeks=0,
                days=0,
                hours=0,
                minutes=0,
                seconds=0,
                milliseconds=0,
                microseconds=0,
            ),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="json_col",
        db_column_name="json_col",
        column_class_name="JSON",
        column_class=JSON,
        params={
            "default": "{}",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="jsonb_col",
        db_column_name="jsonb_col",
        column_class_name="JSONB",
        column_class=JSONB,
        params={
            "default": "{}",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="numeric_col",
        db_column_name="numeric_col",
        column_class_name="Numeric",
        column_class=Numeric,
        params={
            "default": decimal.Decimal("0"),
            "digits": (5, 2),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="real_col",
        db_column_name="real_col",
        column_class_name="Real",
        column_class=Real,
        params={
            "default": 0.0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="double_precision_col",
        db_column_name="double_precision_col",
        column_class_name="DoublePrecision",
        column_class=DoublePrecision,
        params={
            "default": 0.0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="smallint_col",
        db_column_name="smallint_col",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="text_col",
        db_column_name="text_col",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="timestamp_col",
        db_column_name="timestamp_col",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="timestamptz_col",
        db_column_name="timestamptz_col",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="uuid_col",
        db_column_name="uuid_col",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="varchar_col",
        db_column_name="varchar_col",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="unique_col",
        db_column_name="unique_col",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="null_col",
        db_column_name="null_col",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="MegaTable",
        tablename="mega_table",
        column_name="not_null_col",
        db_column_name="not_null_col",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
