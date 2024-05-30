import contextvars
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence
from piccolo.engine.base import Engine, validate_savepoint_name
from psqlpy import ConnectionPool, Connection, Transaction, Cursor
from psqlpy.exceptions import RustPSQLDriverPyBaseError
from piccolo.utils.warnings import Level, colored_warning
from piccolo.query.base import DDL, Query
from piccolo.engine.base import Batch
from piccolo.querystring import QueryString
from piccolo.utils.sync import run_sync
from piccolo.engine.exceptions import TransactionError


@dataclass
class AsyncBatch(Batch):
    connection: Connection
    query: Query
    batch_size: int

    # Set internally
    _transaction: Optional[Transaction] = None
    _cursor: Optional[Cursor] = None

    @property
    def cursor(self) -> Cursor:
        if not self._cursor:
            raise ValueError("_cursor not set")
        return self._cursor

    async def next(self) -> List[Dict]:
        data = await self.cursor.fetch(self.batch_size)
        return await self.query._process_results(data.result())

    def __aiter__(self):
        return self

    async def __anext__(self):
        response = await self.next()
        if response == []:
            raise StopAsyncIteration()
        return response

    async def __aenter__(self):
        transaction = self.connection.transaction()
        self._transaction = transaction
        await self._transaction.begin()
        querystring = self.query.querystrings[0]
        template, template_args = querystring.compile_string()

        self._cursor = await transaction.cursor(
            querystring=template,
            parameters=template_args,
        )
        return self

    async def __aexit__(self, exception_type, exception, traceback):
        if exception:
            await self._transaction.rollback()
        else:
            await self._transaction.commit()

        return exception is not None


class Savepoint:
    def __init__(self, name: str, transaction: "PostgresTransaction"):
        self.name = name
        self.transaction = transaction

    async def rollback_to(self):
        validate_savepoint_name(self.name)
        await self.transaction.connection.execute(
            f"ROLLBACK TO SAVEPOINT {self.name}"
        )

    async def release(self):
        validate_savepoint_name(self.name)
        await self.transaction.connection.execute(
            f"RELEASE SAVEPOINT {self.name}"
        )


class PostgresTransaction:
    def __init__(self, engine: "PSQLPyEngine", allow_nested: bool = True) -> None:
        self.engine = engine
        current_transaction = self.engine.current_transaction.get()

        self._savepoint_id = 0
        self._parent = None
        self._committed = False
        self._rolled_back = False

        if current_transaction:
            if allow_nested:
                self._parent = current_transaction
            else:
                raise TransactionError(
                    "A transaction is already active - nested transactions "
                    "aren't allowed."
                )
    
    async def __aenter__(self) -> "PostgresTransaction":
        if self._parent is not None:
            return self._parent

        self.connection = await self.get_connection()
        self.transaction = self.connection.transaction()
        await self.begin()
        self.context = self.engine.current_transaction.set(self)
        return self

    async def get_connection(self):
        if self.engine.pool:
            return await self.engine.pool.connection()
        else:
            return await self.engine.get_new_connection()

    async def begin(self):
        await self.transaction.begin()

    async def commit(self):
        await self.transaction.commit()
        self._committed = True
    
    async def rollback(self):
        await self.transaction.rollback()
        self._rolled_back = True
    
    def get_savepoint_id(self) -> int:
        self._savepoint_id += 1
        return self._savepoint_id

    async def savepoint(self, name: Optional[str] = None) -> Savepoint:
        savepoint_name = name or f"savepoint_{self.get_savepoint_id()}"
        validate_savepoint_name(savepoint_name)
        await self.transaction.create_savepoint(savepoint_name=savepoint_name)
        return Savepoint(name=savepoint_name, transaction=self)

    async def __aexit__(self, exception_type, exception, traceback):
        if self._parent:
            return exception is None

        if exception:
            # The user may have manually rolled it back.
            if not self._rolled_back:
                await self.rollback()
        else:
            # The user may have manually committed it.
            if not self._committed and not self._rolled_back:
                await self.commit()

        self.engine.current_transaction.reset(self.context)

        return exception is None


class PSQLPyEngine(Engine):

    engine_type = "postgres"
    min_version_number = 10
    
    def __init__(
        self,
        config: Dict[str, Any],
        extensions: Sequence[str] = ("uuid-ossp",),
        log_queries: bool = False,
        log_responses: bool = False,
        extra_nodes: Optional[Mapping[str, "PSQLPyEngine"]] = None,
    ) -> None:
        if extra_nodes is None:
            extra_nodes = {}

        self.config = config
        self.extensions = extensions
        self.log_queries = log_queries
        self.log_responses = log_responses
        self.extra_nodes = extra_nodes
        self.pool: Optional[ConnectionPool] = None
        database_name = config.get("database", "Unknown")
        self.current_transaction = contextvars.ContextVar(
            f"pg_current_transaction_{database_name}",
            default=None,
        )
        super().__init__()

    @staticmethod
    def _parse_raw_version_string(version_string: str) -> float:
        """
        The format of the version string isn't always consistent. Sometimes
        it's just the version number e.g. '9.6.18', and sometimes
        it contains specific build information e.g.
        '12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)'. Just extract the major and
        minor version numbers.
        """
        version_segment = version_string.split(" ")[0]
        major, minor = version_segment.split(".")[:2]
        return float(f"{major}.{minor}")

    async def get_version(self) -> float:
        """
        Returns the version of Postgres being run.
        """
        try:
            response: Sequence[Dict] = await self._run_in_new_connection(
                "SHOW server_version"
            )
        except ConnectionRefusedError as exception:
            # Suppressing the exception, otherwise importing piccolo_conf.py
            # containing an engine will raise an ImportError.
            colored_warning(f"Unable to connect to database - {exception}")
            return 0.0
        else:
            version_string = response[0]["server_version"]
            return self._parse_raw_version_string(
                version_string=version_string
            )
    
    def get_version_sync(self) -> float:
        return run_sync(self.get_version())

    async def prep_database(self):
        for extension in self.extensions:
            try:
                await self._run_in_new_connection(
                    f'CREATE EXTENSION IF NOT EXISTS "{extension}"',
                )
            except RustPSQLDriverPyBaseError:
                colored_warning(
                    f"=> Unable to create {extension} extension - some "
                    "functionality may not behave as expected. Make sure "
                    "your database user has permission to create "
                    "extensions, or add it manually using "
                    f'`CREATE EXTENSION "{extension}";`',
                    level=Level.medium,
                )
    
    async def start_connnection_pool(self, **kwargs) -> None:
        colored_warning(
            "`start_connnection_pool` is a typo - please change it to "
            "`start_connection_pool`.",
            category=DeprecationWarning,
        )
        return await self.start_connection_pool()

    async def close_connnection_pool(self, **kwargs) -> None:
        colored_warning(
            "`close_connnection_pool` is a typo - please change it to "
            "`close_connection_pool`.",
            category=DeprecationWarning,
        )
        return await self.close_connection_pool()
    
    async def start_connection_pool(self, **kwargs) -> None:
        if self.pool:
            colored_warning(
                "A pool already exists - close it first if you want to create "
                "a new pool.",
            )
        else:
            config = dict(self.config)
            config.update(**kwargs)
            self.pool = ConnectionPool(**config)

    async def close_connection_pool(self) -> None:
        if self.pool:
            self.pool.close()
            self.pool = None
        else:
            colored_warning("No pool is running.")
    
    async def get_new_connection(self) -> Connection:
        """
        Returns a new connection - doesn't retrieve it from the pool.
        """
        return await (ConnectionPool(**dict(self.config))).connection()

    async def batch(
        self,
        query: Query,
        batch_size: int = 100,
        node: Optional[str] = None,
    ) -> AsyncBatch:
        """
        :param query:
            The database query to run.
        :param batch_size:
            How many rows to fetch on each iteration.
        :param node:
            Which node to run the query on (see ``extra_nodes``). If not
            specified, it runs on the main Postgres node.
        """
        engine: Any = self.extra_nodes.get(node) if node else self
        connection = await engine.get_new_connection()
        return AsyncBatch(
            connection=connection, query=query, batch_size=batch_size
        )

    async def _run_in_pool(self, query: str, args: Optional[Sequence[Any]] = None):
        if not self.pool:
            raise ValueError("A pool isn't currently running.")

        connection = await self.pool.connection()
        response = await connection.execute(
            querystring=query,
            parameters=args,
        )

        return response.result()
    
    async def _run_in_new_connection(
        self, query: str, args: Optional[Sequence[Any]] = None
    ):
        if args is None:
            args = []
        connection = await self.get_new_connection()

        try:
            results = await connection.execute(query, *args)
        except RustPSQLDriverPyBaseError as exception:
            raise exception

        return results.result()

    async def run_querystring(
        self, querystring: QueryString, in_pool: bool = True
    ):
        query, query_args = querystring.compile_string(
            engine_type=self.engine_type
        )

        query_id = self.get_query_id()

        if self.log_queries:
            self.print_query(query_id=query_id, query=querystring.__str__())

        # If running inside a transaction:
        current_transaction = self.current_transaction.get()
        if current_transaction:
            response = await current_transaction.connection.fetch(
                query, *query_args
            )
        elif in_pool and self.pool:
            response = await self._run_in_pool(query, query_args)
        else:
            response = await self._run_in_new_connection(query, query_args)

        if self.log_responses:
            self.print_response(query_id=query_id, response=response)

        return response
    
    async def run_ddl(self, ddl: str, in_pool: bool = True):
        query_id = self.get_query_id()

        if self.log_queries:
            self.print_query(query_id=query_id, query=ddl)

        # If running inside a transaction:
        current_transaction = self.current_transaction.get()
        if current_transaction:
            response = await current_transaction.connection.fetch(ddl)
        elif in_pool and self.pool:
            response = await self._run_in_pool(ddl)
        else:
            response = await self._run_in_new_connection(ddl)

        if self.log_responses:
            self.print_response(query_id=query_id, response=response)

        return response

    def atomic(self) -> str:
        return "123"

    def transaction(self, allow_nested: bool = True) -> PostgresTransaction:
        return PostgresTransaction(engine=self, allow_nested=allow_nested)
