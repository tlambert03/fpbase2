from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, cast, overload

from sqlmodel import Session, SQLModel, func, select

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from sqlalchemy.engine import ScalarResult, TupleResult
    from sqlalchemy.sql._typing import _ColumnExpressionArgument
    from sqlmodel.sql.expression import Select, SelectOfScalar

    SingleExpr = _ColumnExpressionArgument[bool] | bool
    MultiExpr = tuple[SingleExpr, ...]
    ColExpression = SingleExpr | MultiExpr

M = TypeVar("M", bound=SQLModel)


class QueryManager(Generic[M]):
    _model: type[M]

    @property
    def _session(self) -> Session:
        if not Manager._session_:
            raise RuntimeError(
                "Session not set, Call `Manager.set_session(session)` "
                "before using Manager methods."
            )
        return Manager._session_

    @overload
    def select(  # type: ignore [overload-overlap]
        self,
        from_: type[M] | None = None,
        limit: int | None = None,
        order_by: Any = None,
        where: ColExpression | None = None,
        exec: Literal[True] = ...,
    ) -> ScalarResult[M]: ...
    @overload
    def select(  # type: ignore [overload-overlap]
        self,
        *entities: Any,
        from_: type[M] | None = None,
        limit: int | None = None,
        order_by: Any = None,
        where: ColExpression | None = None,
        exec: Literal[True] = ...,
    ) -> TupleResult[M]: ...
    @overload
    def select(  # type: ignore [overload-overlap]
        self,
        from_: type[M] | None = None,
        limit: int | None = None,
        order_by: Any = None,
        where: ColExpression | None = None,
        exec: Literal[False] = ...,
    ) -> SelectOfScalar[M]: ...
    @overload
    def select(
        self,
        *entities: Any,
        from_: type[M] | None = None,
        limit: int | None = None,
        order_by: Any = None,
        where: ColExpression | None = None,
        exec: Literal[False] = ...,
    ) -> Select[M]: ...
    def select(
        self,
        *entities: Any,
        from_: type[M] | None = None,
        limit: int | None = None,
        order_by: Any = None,
        where: ColExpression | None = None,
        exec: bool = True,
    ) -> SelectOfScalar[M] | Select[M] | TupleResult[M] | ScalarResult[M]:
        entities = entities or (self._model,)

        statement: Select[M] | SelectOfScalar[M]
        statement = select(*entities).select_from(from_ or self._model)

        if where is not None:
            if not isinstance(where, tuple):
                where = (where,)
            statement = statement.where(*where)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if limit is not None:
            statement = statement.limit(limit)

        if exec:
            return self._session.exec(statement)
        return statement

    def all(self) -> Sequence[M]:
        return self.select(limit=None).all()

    def count(self) -> int:
        statement = select([func.count()]).select_from(self._model)
        return cast(int, self._session.exec(statement).one())

    @overload
    def first(self, raises: Literal[True] = True) -> M: ...
    @overload
    def first(self, raises: Literal[False]) -> M | None: ...
    def first(self, raises: bool = True) -> M | None:
        if raises:
            return self.select(limit=1).one()
        return self.select(limit=1).first()

    @overload
    def random(self, n: Literal[1] = 1) -> M:  # type: ignore [overload-overlap]
        ...
    @overload
    def random(self, n: int) -> Sequence[M]: ...
    def random(self, n: int = 1) -> M | Sequence[M]:
        result = self.select(limit=n, order_by=func.random())
        if n == 1:
            return result.one()
        return result.all()

    # TODO: Unpack kwargs from ModelCreateType
    @overload
    def where(  # type: ignore [overload-overlap]
        self, *clauses: SingleExpr | dict, limit: Literal[1], **kwargs: Any
    ) -> M: ...
    @overload
    def where(
        self, *clauses: SingleExpr | dict, limit: int | None = ..., **kwargs: Any
    ) -> Sequence[M]: ...
    def where(
        self, *clauses: SingleExpr | dict, limit: int | None = None, **kwargs: Any
    ) -> M | Sequence[M] | None:
        where: list[SingleExpr] = []
        for clause in clauses:
            if isinstance(clause, dict):
                where.extend(self._dict_to_expr(clause))
            else:
                where.append(clause)
        where.extend(self._dict_to_expr(kwargs))

        result = self.select(limit=limit, where=tuple(where))
        if limit == 1:
            return result.first()
        return result.all()

    def _dict_to_expr(self, d: dict[str, Any]) -> Iterator[SingleExpr]:
        return (getattr(self._model, k) == v for k, v in d.items())

    @overload
    def get(self, ident: Any, raises: Literal[True] = True) -> M: ...
    @overload
    def get(self, ident: Any, raises: Literal[False]) -> M | None: ...
    def get(self, ident: Any, raises: bool = True) -> M | None:
        if (obj := self._session.get(self._model, ident)) is None:
            if raises:
                raise KeyError(
                    f"Cannot find {self._model.__name__} with primary_key '{ident}'"
                )
        return obj

    # TODO: collect ReadType or CreateType generics to parameterize args

    def get_or_create(self, **kwargs: Any) -> M:
        if (obj := self.where(kwargs, limit=1)) is not None:
            return obj
        return self.create(**kwargs)

    def create(self, obj: Any | None = None, **kwargs: Any) -> M:
        db_obj = self._model.model_validate(obj or kwargs)
        self._session.add(db_obj)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        self._session.refresh(db_obj)
        return db_obj


class Manager(Generic[M]):
    # FIXME: figure out better injection logic for session
    _session_: Session | None = None

    @classmethod
    def set_session(cls, session: Session) -> None:
        cls._session_ = session

    def __init__(self) -> None:
        self._qm: QueryManager[M] | None = None

    def __get__(self, instance: M | None, owner: type[M]) -> QueryManager[M]:
        if instance is not None:
            raise AttributeError("QueryDescriptor is only accessible from the class")
        if self._qm is None:
            self._qm = self._create_query_manager(owner)
        return self._qm

    def _create_query_manager(self, model: type[M]) -> QueryManager[M]:
        newtype = type(f"{model.__name__}Manager", (QueryManager,), {"_model": model})()
        return cast(QueryManager[M], newtype)
