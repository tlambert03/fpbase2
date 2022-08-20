from typing import Any

from sqlmodel import SQLModel as _SQLModel
from sqlmodel.main import SQLModelMetaclass as _SQLModelMetaclass


class SQLModelMetaclass(_SQLModelMetaclass):
    def __new__(
        cls,
        name: str,
        bases: tuple[type[Any], ...],
        class_dict: dict[str, Any],
        **kwargs: Any
    ) -> Any:
        new_cls = super().__new__(cls, name, bases, class_dict, **kwargs)

        # preserve `__set_name__` protocol defined in https://peps.python.org/pep-0487
        # see https://github.com/pydantic/pydantic/pull/4407
        for name, obj in class_dict.items():
            set_name = getattr(obj, "__set_name__", None)
            if callable(set_name):
                set_name(new_cls, name)

        return new_cls


class SQLModel(_SQLModel, metaclass=SQLModelMetaclass):
    ...
