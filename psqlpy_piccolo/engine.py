from __future__ import annotations
import contextvars
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generator, Mapping, Sequence

from piccolo.engine.base import BaseBatch, Engine, validate_savepoint_name
from piccolo.engine.exceptions import TransactionError
from piccolo.query.base import DDL, Query
from piccolo.utils.sync import run_sync
from piccolo.utils.warnings import Level, colored_warning
from psqlpy import Connection, ConnectionPool, Cursor, Transaction
from psqlpy.exceptions import RustPSQLDriverPyBaseError
from typing_extensions import Self


if TYPE_CHECKING:
    import types

    from piccolo.querystring import QueryString


@dataclass
class AsyncBatch(BaseBatch):
    """PostgreSQL `Cursor` representation in Python."""

    connection: Connection
    query: Query[Any, Any]
    batch_size: int

    # Set internally
    _transaction: Transaction | None = None
    _cursor: Cursor | None = None

    @property
    def cursor(self) -> Cursor:
        """Return Python object which represents PostgreSQL `Cursor`.

        ### Returns:
        - `Cursor` object.
        """
        if not self._cursor:
            raise ValueError("_cursor not set")
        return self._cursor

    async def next(self) -> list[dict[str, Any]]:
        """Retrieve next batch from the Cursor.

        ### Returns:
        list of dicts of results.
        """
        data = await self.cursor.fetch(self.batch_size)
        return data.result()

    def __aiter__(self: Self) -> Self:
        return self

    async def __anext__(self: Self) -> list[dict[str, Any]]:
        response = await self.next()
        if response == []:
            raise StopAsyncIteration
        return response

    async def __aenter__(self: Self) -> Self:
        transaction = self.connection.transaction()
        self._transaction = transaction
        await self._transaction.begin()
        querystring = self.query.querystrings[0]
        template, template_args = querystring.compile_string()

        self._cursor = transaction.cursor(
            querystring=template,
            parameters=template_args,
        )
        return self

    async def __aexit__(
        self: Self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> bool:
        if exception:
            await self._transaction.rollback()  # type: ignore[union-attr]
        else:
            await self._transaction.commit()  # type: ignore[union-attr]

        return exception is not None


class Atomic:
    """Useful if you want to build up a transaction programmatically.

    Usage::

        transaction = engine.atomic()
        transaction.add(Foo.create_table())

        # Either:
        transaction.run_sync()
        await transaction.run()

    """

    __slots__ = ("engine", "queries")

    def __init__(self: Self, engine: PSQLPyEngine) -> None:
        """Initialize programmatically configured atomic transaction.

        ### Parameters:
        - `engine`: engine for query executing.
        """
        self.engine = engine
        self.queries: list[Query[Any, Any] | DDL] = []

    def __await__(self: Self) -> Generator[Any, None, None]:
        return self.run().__await__()

    def add(self: Self, *query: Query[Any, Any] | DDL) -> None:
        """Add query to atomic transaction.

        ### Params:
        - `query`: new query to add.
        """
        self.queries += list(query)

    async def run(self: Self) -> None:
        """Run a transaction with all added queries."""
        from piccolo.query.methods.objects import Create, GetOrCreate

        try:
            async with self.engine.transaction():
                for query in self.queries:
                    if isinstance(query, (Query, DDL, Create, GetOrCreate)):
                        await query.run()
                    else:
                        raise TypeError("Unrecognised query")  # noqa: TRY301
            self.queries = []
        except Exception as exception:
            self.queries = []
            raise exception from exception

    def run_sync(self: Self) -> None:
        """Run a transaction with all added queries in sync context."""
        return run_sync(self.run())


class Savepoint:
    """PostgreSQL `SAVEPOINT` representation in Python."""

    def __init__(self: Self, name: str, transaction: PostgresTransaction) -> None:
        """Initialize new `SAVEPOINT`.

        ### Parameters:
        - `name`: name of the savepoint.
        - `transaction`: transaction for savepoint.
        """
        self.name = name
        self.transaction = transaction

    async def rollback_to(self: Self) -> None:
        """Rollback transaction to current savepoint."""
        validate_savepoint_name(self.name)
        await self.transaction.connection.execute(f"ROLLBACK TO SAVEPOINT {self.name}")

    async def release(self: Self) -> None:
        """Release savepoint.

        The same name of this savepoint can be used one more time.
        """
        validate_savepoint_name(self.name)
        await self.transaction.connection.execute(f"RELEASE SAVEPOINT {self.name}")


class PostgresTransaction:
    """Used for wrapping queries in a transaction, using a context manager.

    Currently it's async only.

    Usage::

        async with engine.transaction():
            # Run some queries:
            await Band.select().run()

    """

    def __init__(self: Self, engine: PSQLPyEngine, allow_nested: bool = True) -> None:
        """Initialize new transaction.

        ### Parameters:
        - `engine`: engine for the transaction.
        - `allow_nested`: is nested transactions are allowed.
        """
        self.engine = engine
        current_transaction = self.engine.current_transaction.get()
        self.connection: Connection

        self._savepoint_id = 0
        self._parent = None
        self._committed = False
        self._rolled_back = False

        if current_transaction:
            if allow_nested:
                self._parent = current_transaction
            else:
                raise TransactionError(
                    "A transaction is already active - nested transactions aren't allowed.",
                )

    async def __aenter__(self: Self) -> Self:
        if self._parent is not None:
            return self._parent

        self.connection = await self.get_connection()
        self.transaction = self.connection.transaction()
        await self.begin()
        self.context = self.engine.current_transaction.set(
            self,  # type: ignore[arg-type]
        )
        return self

    async def __aexit__(
        self: Self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> bool:
        if self._parent:
            return exception is None

        if exception:
            # The user may have manually rolled it back.
            if not self._rolled_back:
                await self.rollback()
        else:  # noqa: PLR5501
            # The user may have manually committed it.
            if not self._committed and not self._rolled_back:
                await self.commit()

        self.engine.current_transaction.reset(self.context)

        return exception is None

    async def get_connection(self: Self) -> Connection:
        """Retrieve new connection.

        If there is a pool, return connection from the pool.
        Otherwise, retrieve new connection and return it.
        """
        if self.engine.pool:
            return await self.engine.pool.connection()
        return await self.engine.get_new_connection()

    async def begin(self: Self) -> None:
        """Start the transaction."""
        await self.transaction.begin()

    async def commit(self: Self) -> None:
        """Commit the transaction."""
        await self.transaction.commit()
        self._committed = True

    async def rollback(self: Self) -> None:
        """Rollback the transaction."""
        await self.transaction.rollback()
        self._rolled_back = True

    def get_savepoint_id(self: Self) -> int:
        """Retrieve new savepoint id.

        ### Returns:
        new savepoint ID.
        """
        self._savepoint_id += 1
        return self._savepoint_id

    async def rollback_to(self, savepoint_name: str) -> None:
        """Use to rollback to a savepoint just using the name."""
        await Savepoint(name=savepoint_name, transaction=self).rollback_to()

    async def savepoint(self: Self, name: str | None = None) -> Savepoint:
        """Create new savepoint.

        ### Parameters:
        - `name`: name for the savepoint.

        ### Returns:
        New `Savepoint` object.
        """
        savepoint_name = name or f"savepoint_{self.get_savepoint_id()}"
        validate_savepoint_name(savepoint_name)
        await self.transaction.create_savepoint(savepoint_name=savepoint_name)
        return Savepoint(name=savepoint_name, transaction=self)


class PSQLPyEngine(Engine[PostgresTransaction]):
    """Engine for PostgreSQL.

    ### Params:
    - `config`:
        The config dictionary is passed to the underlying database adapter,
        psqlpy. Common arguments you're likely to need are:

        * host
        * port
        * user
        * password
        * database

        For example, ``{'host': 'localhost', 'port': 5432}``.

        See the `asyncpg docs <https://magicstack.github.io/asyncpg/current/api/index.html#connection>`_
        for all available options.

    - `extensions`:
        When the engine starts, it will try and create these extensions
        in Postgres. If you're using a read only database, set this value to an
        empty tuple ``()``.

    - `log_queries`:
        If ``True``, all SQL and DDL statements are printed out before being
        run. Useful for debugging.

    - `log_responses`:
        If ``True``, the raw response from each query is printed out. Useful
        for debugging.

    - `extra_nodes`:
        If you have additional database nodes (e.g. read replicas) for the
        server, you can specify them here. It's a mapping of a memorable name
        to a ``PSQLPyEngine`` instance. For example::

            DB = PSQLPyEngine(
                config={"database": "main_db"},
                extra_nodes={
                    "read_replica_1": PSQLPyEngine(
                        config={"database": "main_db", host: "read_replicate.my_db.com"}, extensions=()
                    )
                },
            )

        Note how we set ``extensions=()``, because it's a read only database.

        When executing a query, you can specify one of these nodes instead
        of the main database. For example::

            >>> await MyTable.select().run(node="read_replica_1")

    """

    engine_type = "postgres"
    min_version_number = 10

    def __init__(
        self: Self,
        config: dict[str, Any],
        extensions: Sequence[str] = ("uuid-ossp",),
        log_queries: bool = False,
        log_responses: bool = False,
        extra_nodes: Mapping[str, PSQLPyEngine] | None = None,
    ) -> None:
        """Initialize `PSQLPyEngine`.

            ### Params:
        - `config`:
            The config dictionary is passed to the underlying database adapter,
            asyncpg. Common arguments you're likely to need are:

            * host
            * port
            * user
            * password
            * database

            For example, ``{'host': 'localhost', 'port': 5432}``.

            See the `asyncpg docs <https://magicstack.github.io/asyncpg/current/api/index.html#connection>`_
            for all available options.

        - `extensions`:
            When the engine starts, it will try and create these extensions
            in Postgres. If you're using a read only database, set this value to an
            empty tuple ``()``.

        - `log_queries`:
            If ``True``, all SQL and DDL statements are printed out before being
            run. Useful for debugging.

        - `log_responses`:
            If ``True``, the raw response from each query is printed out. Useful
            for debugging.

        - `extra_nodes`:
            If you have additional database nodes (e.g. read replicas) for the
            server, you can specify them here. It's a mapping of a memorable name
            to a ``PSQLPyEngine`` instance. For example::

                DB = PSQLPyEngine(
                    config={"database": "main_db"},
                    extra_nodes={
                        "read_replica_1": PSQLPyEngine(
                            config={"database": "main_db", host: "read_replicate.my_db.com"}, extensions=()
                        )
                    },
                )

            Note how we set ``extensions=()``, because it's a read only database.

            When executing a query, you can specify one of these nodes instead
            of the main database. For example::

                >>> await MyTable.select().run(node="read_replica_1")
        """
        if extra_nodes is None:
            extra_nodes = {}

        self.config = config
        self.extensions = extensions
        self.log_queries = log_queries
        self.log_responses = log_responses
        self.extra_nodes = extra_nodes
        self.pool: ConnectionPool | None = None
        database_name = config.get("database", "Unknown")
        self.current_transaction = contextvars.ContextVar(
            f"pg_current_transaction_{database_name}",
            default=None,
        )
        super().__init__(
            engine_type=self.engine_type,
            min_version_number=self.min_version_number,
        )

    @staticmethod
    def _parse_raw_version_string(version_string: str) -> float:
        """Parse version came from PostgreSQL.

        The format of the version string isn't always consistent. Sometimes
        it's just the version number e.g. '9.6.18', and sometimes
        it contains specific build information e.g.
        '12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)'. Just extract the major and
        minor version numbers.
        """
        version_segment = version_string.split(" ")[0]
        major, minor = version_segment.split(".")[:2]
        return float(f"{major}.{minor}")

    async def get_version(self: Self) -> float:
        """Retrieve the version of Postgres being run."""
        try:
            response: Sequence[dict[str, Any]] = await self._run_in_new_connection(
                "SHOW server_version",
            )
        except ConnectionRefusedError as exception:
            # Suppressing the exception, otherwise importing piccolo_conf.py
            # containing an engine will raise an ImportError.
            colored_warning(f"Unable to connect to database - {exception}")
            return 0.0
        else:
            version_string = response[0]["server_version"]
            return self._parse_raw_version_string(version_string=version_string)

    def get_version_sync(self: Self) -> float:
        """Retrieve the version of Postgres being run in sync way."""
        return run_sync(self.get_version())

    async def prep_database(self: Self) -> None:
        """Prepare database before use.

        Create all extensions specified in configuration.
        """
        for extension in self.extensions:
            try:
                await self._run_in_new_connection(
                    f'CREATE EXTENSION IF NOT EXISTS "{extension}"',
                )
            except RustPSQLDriverPyBaseError:  # noqa: PERF203
                colored_warning(
                    f"=> Unable to create {extension} extension - some "
                    "functionality may not behave as expected. Make sure "
                    "your database user has permission to create "
                    "extensions, or add it manually using "
                    f'`CREATE EXTENSION "{extension}";`',
                    level=Level.medium,
                )

    async def start_connnection_pool(
        self: Self,
        **_kwargs: dict[str, Any],
    ) -> None:
        """Start new connection pool.

        Create and start new connection pool.
        If connection pool already exists do nothing.

        ### Parameters:
        - `kwargs`: configuration parameters for `ConnectionPool` from PSQLPy.
        """
        colored_warning(
            "`start_connnection_pool` is a typo - please change it to `start_connection_pool`.",
            category=DeprecationWarning,
        )
        return await self.start_connection_pool()

    async def close_connnection_pool(self: Self, **_kwargs: dict[str, Any]) -> None:
        """Close connection pool."""
        colored_warning(
            "`close_connnection_pool` is a typo - please change it to `close_connection_pool`.",
            category=DeprecationWarning,
        )
        return await self.close_connection_pool()

    async def start_connection_pool(self: Self, **kwargs: dict[str, Any]) -> None:
        """Start new connection pool.

        Create and start new connection pool.
        If connection pool already exists do nothing.

        ### Parameters:
        - `kwargs`: configuration parameters for `ConnectionPool` from PSQLPy.
        """
        if self.pool:
            colored_warning(
                "A pool already exists - close it first if you want to create a new pool.",
            )
        else:
            config = dict(self.config)
            config.update(**kwargs)
            self.pool = ConnectionPool(
                db_name=config.pop("database", None),
                username=config.pop("user", None),
                max_db_pool_size=config.pop("max_size", 2),
                **config,
            )

    async def close_connection_pool(self) -> None:
        """Close connection pool."""
        if self.pool:
            self.pool.close()
            self.pool = None
        else:
            colored_warning("No pool is running.")

    async def get_new_connection(self) -> Connection:
        """Return a new connection - doesn't retrieve it from the pool."""
        if self.pool:
            return await self.pool.connection()

        config = dict(self.config)
        return await (
            ConnectionPool(
                db_name=config.pop("database", None),
                username=config.pop("user", None),
                **config,
            )
        ).connection()

    def transform_response_to_dicts(
        self,
        results: list[dict[str, Any]] | dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Transform result to list of dicts."""
        if isinstance(results, list):
            return results

        return [results]

    async def batch(
        self: Self,
        query: Query[Any, Any],
        batch_size: int = 100,
        node: str | None = None,
    ) -> AsyncBatch:
        """Create new `AsyncBatch`.

        It allows you to retrieve results of your query in batches.

        ### Parameters:
        - `query`:
            The database query to run.
        - `batch_size`:
            How many rows to fetch on each iteration.
        - `node`:
            Which node to run the query on (see ``extra_nodes``). If not
            specified, it runs on the main Postgres node.
        """
        engine: Any = self.extra_nodes.get(node) if node else self
        connection = await engine.get_new_connection()
        return AsyncBatch(connection=connection, query=query, batch_size=batch_size)

    async def _run_in_pool(
        self: Self,
        query: str,
        args: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run query in the pool.

        ### Parameters:
        - `query`: query to execute.
        - `args`: arguments for the query.

        ### Returns:
        Result from the database as a list of dicts.
        """
        if not self.pool:
            raise ValueError("A pool isn't currently running.")

        connection = await self.pool.connection()
        response = await connection.execute(
            querystring=query,
            parameters=args,
        )

        return response.result()

    async def _run_in_new_connection(
        self: Self,
        query: str,
        args: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run query in a new connection.

        ### Parameters:
        - `query`: query to execute.
        - `args`: arguments for the query.

        ### Returns:
        Result from the database as a list of dicts.
        """
        connection = await self.get_new_connection()
        results = await connection.execute(
            querystring=query,
            parameters=args,
        )
        connection.back_to_pool()

        return results.result()

    async def run_querystring(
        self: Self,
        querystring: QueryString,
        in_pool: bool = True,
    ) -> list[dict[str, Any]]:
        """Run querystring.

        ### Parameters:
        - `querystring`: querystring to execute.
        - `in_pool`: execute in pool or not.

        ### Returns:
        Result from the database as a list of dicts.
        """
        query, query_args = querystring.compile_string(engine_type=self.engine_type)

        query_id = self.get_query_id()

        if self.log_queries:
            self.print_query(query_id=query_id, query=querystring.__str__())
        # If running inside a transaction:
        current_transaction = self.current_transaction.get()
        if current_transaction:
            raw_response = await current_transaction.connection.fetch(
                querystring=query,
                parameters=query_args,
            )
            response = raw_response.result()
        elif in_pool and self.pool:
            response = await self._run_in_pool(query, query_args)
        else:
            response = await self._run_in_new_connection(query, query_args)

        if self.log_responses:
            self.print_response(query_id=query_id, response=response)

        return response

    async def run_ddl(
        self: Self,
        ddl: str,
        in_pool: bool = True,
    ) -> list[dict[str, Any]]:
        """Run ddl query.

        ### Parameters:
        - `ddl`: ddl to execute.
        - `in_pool`: execute in pool or not.
        """
        query_id = self.get_query_id()

        if self.log_queries:
            self.print_query(query_id=query_id, query=ddl)

        # If running inside a transaction:
        current_transaction = self.current_transaction.get()
        if current_transaction:
            raw_response = await current_transaction.connection.fetch(ddl)
            response = raw_response.result()
        elif in_pool and self.pool:
            response = await self._run_in_pool(ddl)
        else:
            response = await self._run_in_new_connection(ddl)

        if self.log_responses:
            self.print_response(query_id=query_id, response=response)

        return response

    def atomic(self: Self) -> Atomic:
        """Create new `Atomic` object.

        ### Returns:
        New `Atomic` object to build up a transaction programmatically.
        """
        return Atomic(engine=self)

    def transaction(self: Self, allow_nested: bool = True) -> PostgresTransaction:
        """Create new `PostgresTransaction` object.

        ### Parameters:
        - `allow_nested`: is nested transactions are allowed.

        ### Returns:
        New instance of `PostgresTransaction`.
        """
        return PostgresTransaction(engine=self, allow_nested=allow_nested)
