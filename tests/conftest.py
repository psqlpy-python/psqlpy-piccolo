import asyncio
import typing
from unittest.mock import MagicMock

import pytest

from tests.test_apps.mega.tables import MegaTable, SmallTable
from tests.test_apps.music.tables import (
    Band,
    Concert,
    Instrument,
    Manager,
    Poster,
    RecordingStudio,
    Shirt,
    Ticket,
    Venue,
)


if typing.TYPE_CHECKING:
    from piccolo.table import Table

pytestmark = [pytest.mark.anyio]


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
async def _clean_up() -> None:
    tables_to_clean: typing.Final[list[Table]] = [
        MegaTable,
        SmallTable,
        Manager,
        Band,
        Venue,
        Concert,
        Ticket,
        Poster,
        Shirt,
        RecordingStudio,
        Instrument,
    ]
    for table_to_clean in tables_to_clean:
        await table_to_clean.delete(force=True)


class AsyncMock(MagicMock):
    """Async MagicMock for python 3.7+.

    This is a workaround for the fact that MagicMock is not async compatible in
    Python 3.7.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)

        # this makes asyncio.iscoroutinefunction(AsyncMock()) return True
        self._is_coroutine = asyncio.coroutines.iscoroutine

    async def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: ANN401
        return super(AsyncMock, self).__call__(*args, **kwargs)  # noqa: UP008
