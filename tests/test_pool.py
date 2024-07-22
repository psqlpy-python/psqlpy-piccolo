import asyncio
import os
import tempfile
import typing
from unittest.mock import call, patch

from piccolo.engine.sqlite import SQLiteEngine

from psqlpy_piccolo import PSQLPyEngine
from tests.test_apps.music.tables import Manager


async def test_create_pool() -> None:
    engine: typing.Final = typing.cast(PSQLPyEngine, Manager._meta.db)

    await engine.start_connection_pool()
    assert engine.pool is not None

    await engine.close_connection_pool()
    assert engine.pool is None


async def test_make_query() -> None:
    await Manager._meta.db.start_connection_pool()

    await Manager(name="Bob").save().run()
    response = await Manager.select().run()
    assert "Bob" in [instance["name"] for instance in response]

    await Manager._meta.db.close_connection_pool()


async def test_make_many_queries() -> None:
    await Manager._meta.db.start_connection_pool()

    await Manager(name="Bob").save().run()

    async def get_data() -> None:
        response = await Manager.select().run()
        assert response[0]["name"] == "Bob"

    await asyncio.gather(*[get_data() for _ in range(500)])

    await Manager._meta.db.close_connection_pool()


async def test_proxy_methods() -> None:
    engine: typing.Final = typing.cast(PSQLPyEngine, Manager._meta.db)

    # Deliberate typo ('nnn'):
    await engine.start_connnection_pool()
    assert engine.pool is not None

    # Deliberate typo ('nnn'):
    await engine.close_connnection_pool()
    assert engine.pool is None


async def test_warnings() -> None:
    sqlite_file = os.path.join(tempfile.gettempdir(), "engine.sqlite")  # noqa: PTH118
    engine = SQLiteEngine(path=sqlite_file)

    with patch("piccolo.engine.base.colored_warning") as colored_warning:
        await engine.start_connection_pool()
        await engine.close_connection_pool()

        assert colored_warning.call_args_list == [
            call(
                "Connection pooling is not supported for sqlite.",
                stacklevel=3,
            ),
            call(
                "Connection pooling is not supported for sqlite.",
                stacklevel=3,
            ),
        ]
