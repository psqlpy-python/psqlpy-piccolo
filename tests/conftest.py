import pytest

pytestmark = [pytest.mark.anyio]


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"
