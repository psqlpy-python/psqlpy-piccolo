from __future__ import annotations
import typing

import pytest

from psqlpy_piccolo import PSQLPyEngine
from tests.test_apps.music.tables import Band, Manager


def test_atomic_error_statement() -> None:
    """Make sure queries in a transaction aren't committed if a query fails."""
    atomic = Band._meta.db.atomic()
    atomic.add(
        Band.raw("MALFORMED QUERY ... SHOULD ERROR"),
    )
    with pytest.raises(Exception):  # noqa: B017, PT011
        atomic.run_sync()


def test_atomic_succeeds_statement() -> None:
    """Make sure that when atomic is run successfully the database is modified accordingly."""
    atomic = Band._meta.db.atomic()
    atomic.add(Manager.insert(Manager(name="test-manager-name")))
    atomic.run_sync()
    assert Manager.count().run_sync() == 1


async def test_atomic_pool() -> None:
    """Make sure atomic works correctly when a connection pool is active."""
    engine = Manager._meta.db
    await engine.start_connection_pool()

    atomic = engine.atomic()
    atomic.add(Manager.insert(Manager(name="test-manager-name")))

    await atomic.run()
    await engine.close_connection_pool()

    assert Manager.count().run_sync() == 1


async def test_transaction_error() -> None:
    """Make sure queries in a transaction aren't committed if a query fails."""
    with pytest.raises(Exception):  # noqa: B017, PT011, PT012
        async with Manager._meta.db.transaction():
            await Manager.insert(Manager(name="test-manager-name"))
            await Manager.raw("MALFORMED QUERY ... SHOULD ERROR")

    assert Manager.count().run_sync() == 0


async def test_transaction_succeeds() -> None:
    async with Manager._meta.db.transaction():
        await Manager.insert(Manager(name="test-manager-name"))

    assert Manager.count().run_sync() == 1


async def test_transaction_manual_commit() -> None:
    async with Band._meta.db.transaction() as transaction:
        await Manager.insert(Manager(name="test-manager-name"))
        await transaction.commit()

    assert Manager.count().run_sync() == 1


async def test_transaction_manual_rollback() -> None:
    async with Band._meta.db.transaction() as transaction:
        await Manager.insert(Manager(name="test-manager-name"))
        await transaction.rollback()

    assert Manager.count().run_sync() == 0


async def test_transaction_id() -> None:
    """An extra sanity check, that the transaction id is the same for each query inside the transaction block."""

    async def get_transaction_ids() -> list[str]:
        responses = []
        async with Band._meta.db.transaction():
            responses.append(await Manager.raw("SELECT txid_current()").run())
            responses.append(await Manager.raw("SELECT txid_current()").run())

        return [response[0]["txid_current"] for response in responses]

    transaction_ids: typing.Final = await get_transaction_ids()
    assert len(set(transaction_ids)) == 1

    next_transaction_ids: typing.Final = await get_transaction_ids()
    assert len(set(next_transaction_ids)) == 1
    assert next_transaction_ids[0] != transaction_ids[0]


async def test_transaction_exists() -> None:
    """Make sure we can detect when code is within a transaction."""
    engine: typing.Final = typing.cast(PSQLPyEngine, Manager._meta.db)

    async with engine.transaction():
        assert engine.transaction_exists()

    assert not engine.transaction_exists()


async def test_transaction_savepoint() -> None:
    async with Manager._meta.db.transaction() as transaction:
        await Manager.insert(Manager(name="Manager 1"))
        savepoint = await transaction.savepoint()
        await Manager.insert(Manager(name="Manager 2"))
        await savepoint.rollback_to()

        assert await Manager.select(Manager.name).run() == [{"name": "Manager 1"}]


async def test_transaction_named_savepoint() -> None:
    async with Manager._meta.db.transaction() as transaction:
        await Manager.insert(Manager(name="Manager 1"))
        await transaction.savepoint("my_savepoint1")
        await Manager.insert(Manager(name="Manager 2"))
        await transaction.savepoint("my_savepoint2")
        await Manager.insert(Manager(name="Manager 3"))
        await transaction.rollback_to("my_savepoint1")

        assert await Manager.select(Manager.name).run() == [{"name": "Manager 1"}]


async def test_savepoint_sqli_checks() -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        async with Manager._meta.db.transaction() as transaction:
            await transaction.savepoint(
                "my_savepoint; SELECT * FROM Manager",
            )
