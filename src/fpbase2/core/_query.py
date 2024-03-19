from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    TypeVar,
    cast,
    overload,
)

from sqlmodel import Session, SQLModel, func, select

from fpbase2.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.future import Engine
    from sqlalchemy.sql.elements import ColumnElement


M = TypeVar("M", bound=SQLModel)
_SESSIONS: dict[str, Session] = {}


class QueryManager(Generic[M]):
    """Convenience accessor for SQLModel queries.

    Methods include:
        all: Return all rows.
        cout: Return the number of rows.
        first: Return the first row.
        random(n=1): Return a random row or rows.
        where(expression, limit=1): Return rows matching the expression.
        get(id): Return the row with the given id.
        create(**kwargs): Create a new row.

    Examples
    --------
    ```python
    class User(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        name: str
        email: str

        q: ClassVar[QueryDescriptor["User"]] = QueryDescriptor()

    user = User.q.first()
    all_users = User.q.all()
    frank = User.q.where(User.name == "Frank")
    ```
    """

    def __init__(self, model: type[M], engine: Engine | None = None) -> None:
        self._model = model
        if engine is None:
            from fpbase2.core import db

            engine = db.engine

        if str(engine.url) not in _SESSIONS:
            _SESSIONS[str(engine.url)] = Session(engine)
        self.session = _SESSIONS[str(engine.url)]

    @overload
    def _select(
        self, limit: None = ..., order_by: Any = ..., where: ColumnElement | None = ...
    ) -> list[M]: ...
    @overload
    def _select(  # type: ignore[overload-overlap]
        self, limit: Literal[1], order_by: Any = ..., where: ColumnElement | None = ...
    ) -> M: ...
    @overload
    def _select(
        self, limit: int, order_by: Any = ..., where: ColumnElement | None = ...
    ) -> list[M]: ...
    def _select(
        self,
        limit: int | None = None,
        order_by: Any = None,
        where: ColumnElement | None = None,
    ) -> M | Sequence[M] | None:
        statement = select(self._model)
        if where is not None:
            statement = statement.where(where)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if limit == 1:
            return self.session.exec(statement).first()
        elif limit is not None:
            statement = statement.limit(limit)
        return self.session.exec(statement).all()

    def all(self) -> list[M]:
        return self._select(limit=None)

    def count(self) -> int:
        statement = select([func.count()]).select_from(self._model)
        return cast(int, self.session.exec(statement).one())

    def first(self) -> M:
        return self._select(limit=1)

    @overload
    def random(self, n: Literal[1] = 1) -> M:  # type: ignore
        ...

    @overload
    def random(self, n: int) -> list[M]: ...

    def random(self, n: int = 1) -> M | list[M]:
        return self._select(limit=n, order_by=func.random())

    @overload
    def where(  # type: ignore
        self, expression: ColumnElement, limit: Literal[1] = 1
    ) -> M: ...

    @overload
    def where(self, expression: ColumnElement, limit: int | None = None) -> list[M]: ...

    def where(self, expression: ColumnElement, limit: int | None = None) -> M | list[M]:
        return self._select(limit=limit, where=expression)

    @overload
    def get(self, ident: Any, raises: Literal[True] = True) -> M: ...

    @overload
    def get(self, ident: Any, raises: Literal[False]) -> M | None: ...

    def get(self, ident: Any, raises: bool = True) -> M | None:
        # sourcery skip: swap-nested-ifs
        if (obj := self.session.get(self._model, ident)) is None:
            if raises:
                raise KeyError(
                    f"Cannot find {self._model.__name__} with primary_key '{ident}'"
                )
        return obj

    def create(self, session: Session | None = None, **kwargs: Any) -> M:
        db_obj = self._model.model_validate(kwargs)
        session = session or self.session
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


class QueryDescriptor(Generic[M]):
    def __init__(self) -> None:
        self._qm: QueryManager | None = None

    def __get__(self, instance: M, owner: type[M]) -> QueryManager[M]:
        if self._qm is None:
            if settings.ALLOW_QM:
                self._qm = QueryManager(owner)
            else:
                raise RuntimeError("QueryMixin is disabled, set ALLOW_QM=1 to enable")
        return self._qm
