import asyncio
from psqlpy_piccolo.engine import PSQLPyEngine
from piccolo.querystring import QueryString


engine = PSQLPyEngine(
    config={
        "dsn": "postgres://postgres:postgres@localhost:5432/postgres",
    },
)


async def main() -> None:
    await engine.start_connection_pool()
    qs = QueryString(
        "SELECT * FROM users WHERE id = {}",
        3,
    )

    res = await engine.run_querystring(qs)
    print(res)


asyncio.run(main())
