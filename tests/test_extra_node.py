import typing
from unittest.mock import MagicMock

import pytest
from piccolo.columns.column_types import Varchar
from piccolo.engine import engine_finder
from piccolo.table import Table

from psqlpy_piccolo import PSQLPyEngine
from tests.conftest import AsyncMock


# TODO: enable this test, when all discussions here are resolved https://github.com/piccolo-orm/piccolo/issues/986  # noqa: TD002, E501
def skip_test_extra_nodes() -> None:
    """Make sure that other nodes can be queried."""
    test_engine = engine_finder()
    assert test_engine is not None

    test_engine = typing.cast(PSQLPyEngine, test_engine)

    EXTRA_NODE: typing.Final = MagicMock(spec=PSQLPyEngine(config=test_engine.config))  # noqa: N806
    EXTRA_NODE.run_querystring = AsyncMock(return_value=[])

    DB: typing.Final = PSQLPyEngine(  # noqa: N806
        config=test_engine.config,
        extra_nodes={"read_1": EXTRA_NODE},
    )

    class Manager(Table, db=DB):  # type: ignore[call-arg]
        name = Varchar()

    # Make sure the node is queried
    Manager.select().run_sync(node="read_1")
    assert EXTRA_NODE.run_querystring.called

    # Make sure that a non existent node raises an error
    with pytest.raises(KeyError):
        Manager.select().run_sync(node="read_2")
