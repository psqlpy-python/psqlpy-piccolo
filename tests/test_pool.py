import typing

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
