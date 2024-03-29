"""Typed variants of sqlalchemy functions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic.fields import ModelPrivateAttr
from sqlalchemy import event

if TYPE_CHECKING:
    from sqlalchemy.future.engine import Connection
    from sqlalchemy.orm import Mapper


T = TypeVar("T")
C = TypeVar("C", bound=Callable)


# The sqlalchemy.event.listen() function is very flexible regarding targets.
# It generally accepts classes, instances of those classes, and related classes or
# objects from which the appropriate target can be derived.
def listens_for(
    target: Any, identifier: str, *args: Any, **kw: Any
) -> Callable[[C], C]:
    return event.listens_for(target, identifier, *args, **kw)  # type: ignore


# https://docs.sqlalchemy.org/orm/events.html#sqlalchemy.orm.MapperEvents.before_update
def on_before_update(
    target: type[T], *args: Any, **kw: Any
) -> Callable[
    [Callable[[Mapper, Connection, T], Any]], Callable[[Mapper, Connection, T], Any]
]:
    return listens_for(target, "before_update", *args, **kw)


# https://docs.sqlalchemy.org/orm/events.html#sqlalchemy.orm.MapperEvents.before_insert
def on_before_insert(
    target: type[T], *args: Any, **kw: Any
) -> Callable[
    [Callable[[Mapper, Connection, T], Any]], Callable[[Mapper, Connection, T], Any]
]:
    return listens_for(target, "before_insert", *args, **kw)


class EventDecorator(ModelPrivateAttr):
    def __init__(self, fn: Callable, events: Sequence[str] = ()) -> None:
        super().__init__()
        self._fn = fn
        self._event_identifiers = events or getattr(type(self), "_events", ())

    def __set_name__(self, owner: type, name: str) -> None:
        try:
            arglimit: int | None = self._fn.__code__.co_argcount
        except Exception:
            arglimit = None

        def cb(*args: Any) -> Any:
            self._fn(*self._arrange_sqla_args(*args)[:arglimit])

        for ident in self._event_identifiers:
            event.listen(owner, ident, cb)

    def _arrange_sqla_args(self, *args: Any) -> tuple:
        """Optionally rearrange the arguments coming from"""
        return args

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._fn(*args, **kwds)


class on_before_save(EventDecorator):
    _events: ClassVar[list[str]] = ["before_insert", "before_update"]

    def _arrange_sqla_args(self, *args: Any) -> tuple:
        return (args[-1], *args[:2])


# sqlalchemy.orm.MapperEvents
# ---------------------------
# def after_configured(self): ...
# def before_configured(self): ...
# def before_mapper_configured(self, mapper, class_): ...
# def mapper_configured(self, mapper, class_): ...
# def instrument_class(self, mapper, class_): ...
# def after_delete(self, mapper, connection, target): ...
# def after_insert(self, mapper, connection, target): ...
# def after_update(self, mapper, connection, target): ...
# def before_delete(self, mapper, connection, target): ...
# def before_insert(self, mapper, connection, target): ...
# def before_update(self, mapper, connection, target): ...

# sqlalchemy.orm.SessionEvents
# ----------------------------
# def after_attach(self, session, instance): ...
# def after_begin(self, session, transaction, connection): ...
# def after_bulk_delete(self, delete_context): ...
# def after_bulk_update(self, update_context): ...
# def after_commit(self, session): ...
# def after_flush_postexec(self, session, flush_context): ...
# def after_flush(self, session, flush_context): ...
# def after_rollback(self, session): ...
# def after_soft_rollback(self, session, previous_transaction): ...
# def after_transaction_create(self, session, transaction): ...
# def after_transaction_end(self, session, transaction): ...
# def before_attach(self, session, instance): ...
# def before_commit(self, session): ...
# def before_flush(self, session, flush_context, instances): ...
# def deleted_to_detached(self, session, instance): ...
# def deleted_to_persistent(self, session, instance): ...
# def detached_to_persistent(self, session, instance): ...
# def do_orm_execute(self, orm_execute_state): ...
# def loaded_as_persistent(self, session, instance): ...
# def pending_to_persistent(self, session, instance): ...
# def pending_to_transient(self, session, instance): ...
# def persistent_to_deleted(self, session, instance): ...
# def persistent_to_detached(self, session, instance): ...
# def persistent_to_transient(self, session, instance): ...
# def transient_to_pending(self, session, instance): ...
