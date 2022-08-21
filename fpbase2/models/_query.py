from typing import Any, Generic, Literal, TypeVar, overload

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Session, SQLModel, func, select

from ..db import engine

M = TypeVar("M", bound=SQLModel)


class QueryManager(Generic[M]):
    def __init__(self, model: type[M]) -> None:
        self._model = model

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
        with Session(engine) as session:
            statement = select(self._model)
            if where is not None:
                statement = statement.where(where)
            if order_by is not None:
                statement = statement.order_by(order_by)
            if limit == 1:
                return session.exec(statement).first()
            elif limit is not None:
                statement = statement.limit(limit)
            return session.exec(statement).all()

    def all(self) -> list[M]:
        return self._select(limit=None)

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
        with Session(engine) as session:
            # sourcery skip: swap-nested-ifs
            if (obj := session.get(self._model, ident)) is None:
                if raises:
                    raise KeyError(
                        f"Cannot find {self._model.__name__} with primary_key '{ident}'"
                    )
            return obj
