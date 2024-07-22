import pytest
from piccolo.engine.exceptions import TransactionError

from tests.test_apps.music.tables import Manager


async def test_nested_transactions() -> None:
    """Make sure nested transactions databases work as expected."""
    async with Manager._meta.db.transaction():
        await Manager(name="Bob").save().run()

        async with Manager._meta.db.transaction():
            await Manager(name="Dave").save().run()

        assert await Manager.count().run() == 2  # noqa: PLR2004

    assert await Manager.count().run() == 2  # noqa: PLR2004


async def test_nested_transactions_error() -> None:
    """Make sure nested transactions databases work as expected."""
    async with Manager._meta.db.transaction():
        await Manager(name="Bob").save().run()

        with pytest.raises(TransactionError):
            async with Manager._meta.db.transaction(allow_nested=False):
                await Manager(name="Dave").save().run()

        assert await Manager.count().run() == 1

    assert await Manager.count().run() == 1
