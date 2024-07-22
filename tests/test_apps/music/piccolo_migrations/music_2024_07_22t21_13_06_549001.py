import decimal
from enum import Enum

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete, OnUpdate
from piccolo.columns.column_types import (
    JSON,
    JSONB,
    BigInt,
    ForeignKey,
    Integer,
    Numeric,
    Serial,
    Text,
    Varchar,
)
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class Band(Table, tablename="band", schema=None):  # type: ignore[call-arg]
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


class Concert(Table, tablename="concert", schema=None):  # type: ignore[call-arg]
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


class Manager(Table, tablename="manager", schema=None):  # type: ignore[call-arg]
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


class RecordingStudio(Table, tablename="recording_studio", schema=None):  # type: ignore[call-arg]
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


class Venue(Table, tablename="venue", schema=None):  # type: ignore[call-arg]
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


ID = "2024-07-22T21:13:06:549001"
VERSION = "1.14.0"
DESCRIPTION = ""


async def forwards() -> None:
    manager = MigrationManager(
        migration_id=ID,
        app_name="music",
        description=DESCRIPTION,
    )

    manager.add_table(
        class_name="Concert",
        tablename="concert",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Shirt",
        tablename="shirt",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Venue",
        tablename="venue",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Band",
        tablename="band",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Poster",
        tablename="poster",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Manager",
        tablename="manager",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="RecordingStudio",
        tablename="recording_studio",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Instrument",
        tablename="instrument",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Ticket",
        tablename="ticket",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="Concert",
        tablename="concert",
        column_name="band_1",
        db_column_name="band_1",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Band,
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
        table_class_name="Concert",
        tablename="concert",
        column_name="band_2",
        db_column_name="band_2",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Band,
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
        table_class_name="Concert",
        tablename="concert",
        column_name="venue",
        db_column_name="venue",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Venue,
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
        table_class_name="Shirt",
        tablename="shirt",
        column_name="size",
        db_column_name="size",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1,
            "default": "l",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": Enum("Size", {"small": "s", "medium": "m", "large": "l"}),
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Venue",
        tablename="venue",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 100,
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
        table_class_name="Venue",
        tablename="venue",
        column_name="capacity",
        db_column_name="capacity",
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
            "secret": True,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Band",
        tablename="band",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 50,
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
        table_class_name="Band",
        tablename="band",
        column_name="manager",
        db_column_name="manager",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Manager,
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
        table_class_name="Band",
        tablename="band",
        column_name="popularity",
        db_column_name="popularity",
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
        table_class_name="Poster",
        tablename="poster",
        column_name="content",
        db_column_name="content",
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
        table_class_name="Manager",
        tablename="manager",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 50,
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
        table_class_name="RecordingStudio",
        tablename="recording_studio",
        column_name="facilities",
        db_column_name="facilities",
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
        table_class_name="RecordingStudio",
        tablename="recording_studio",
        column_name="facilities_b",
        db_column_name="facilities_b",
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
        table_class_name="Instrument",
        tablename="instrument",
        column_name="name",
        db_column_name="name",
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
        table_class_name="Instrument",
        tablename="instrument",
        column_name="recording_studio",
        db_column_name="recording_studio",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": RecordingStudio,
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
        table_class_name="Ticket",
        tablename="ticket",
        column_name="concert",
        db_column_name="concert",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Concert,
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
        table_class_name="Ticket",
        tablename="ticket",
        column_name="price",
        db_column_name="price",
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

    return manager
