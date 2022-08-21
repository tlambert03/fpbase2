from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, cast, overload

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Session, SQLModel, func, select
from sqlmodel.sql.expression import Select, SelectOfScalar

if TYPE_CHECKING:
    from sqlalchemy.future import Engine


M = TypeVar("M", bound=SQLModel)
_SESSIONS: dict[str, Session] = {}


@lru_cache
def _patch_select() -> None:
    # inherit caching, silence warning
    # https://github.com/tiangolo/sqlmodel/issues/189
    SelectOfScalar.inherit_cache = True  # type: ignore
    Select.inherit_cache = True  # type: ignore


class QueryManager(Generic[M]):
    def __init__(self, model: type[M], engine: Engine | None = None) -> None:
        if engine is None:
            from . import _engine

            engine = _engine.engine

        _patch_select()
        self._model = model
        if str(engine.url) not in _SESSIONS:
            _SESSIONS[str(engine.url)] = Session(engine)
        self.session = _SESSIONS[str(engine.url)]

    @overload
    def _select(  # type: ignore
        self,
        limit: Literal[1] = 1,
        order_by: Any = None,
        where: ColumnElement | None = None,
    ) -> M:
        ...

    @overload
    def _select(
        self,
        limit: Literal[None],
        order_by: Any = None,
        where: ColumnElement | None = None,
    ) -> list[M]:
        ...

    @overload
    def _select(
        self, limit: int, order_by: Any = None, where: ColumnElement | None = None
    ) -> list[M]:
        ...

    def _select(
        self,
        limit: int | None = None,
        order_by: Any = None,
        where: ColumnElement | None = None,
    ) -> M | list[M] | None:
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
    def random(self, n: int) -> list[M]:
        ...

    def random(self, n: int = 1) -> M | list[M]:
        return self._select(limit=n, order_by=func.random())

    def where(self, expression: ColumnElement, limit: int | None = None) -> M | list[M]:
        return self._select(limit=limit, where=expression)

    @overload
    def get(self, ident: Any, raises: Literal[True] = True) -> M:
        ...

    @overload
    def get(self, ident: Any, raises: Literal[False]) -> M | None:
        ...

    def get(self, ident: Any, raises: bool = True) -> M | None:
        # sourcery skip: swap-nested-ifs
        if (obj := self.session.get(self._model, ident)) is None:
            if raises:
                raise KeyError(
                    f"Cannot find {self._model.__name__} with primary_key '{ident}'"
                )
        return obj

    def create(self, **kwargs: Any) -> M:
        db_obj = self._model(**kwargs)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
