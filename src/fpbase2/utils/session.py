from typing import Any, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel

M = TypeVar("M", bound=SQLModel)


def create_object(session: Session, model: type[M], data: BaseModel) -> M:
    """Create an object in the database.

    Parameters
    ----------
    session : Session
        The database session.
    model : type[SQLModel]
        The model to create.
    data : BaseModel
        The data to create the object with.

    Returns
    -------
    SQLModel
        The created instance of the model.
    """
    db_obj = model.model_validate(data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def read_or_404(session: Session, model: type[M], ident: Any, **kwargs: Any) -> M:
    """Read an object from the database or raise a 404 if it doesn't exist.

    Parameters
    ----------
    session : Session
        The database session.
    model : type[SQLModel]
        The model to get.
    ident : Any
        The identifier of the object to get.

    Returns
    -------
    SQLModel
        An instance of the model.

    Raises
    ------
    HTTPException
        If the object doesn't exist.
    """
    if obj := session.get(model, ident, **kwargs):
        return obj
    raise HTTPException(status_code=404, detail=f"{model.__name__} not found")


def update_object(
    session: Session, model: type[M], ident: Any, update_data: BaseModel, **kwargs: Any
) -> M:
    """Update an object in the database.

    Parameters
    ----------
    session : Session
        The database session.
    model : type[SQLModel]
        The model to update.
    ident : Any
        The identifier of the object to get.
    update_data : BaseModel
        The data to update the object with.

    Returns
    -------
    SQLModel
        The updated instance of the model.

    Raises
    ------
    HTTPException
        If the object doesn't exist.
    """
    db_obj = read_or_404(session, model, ident, **kwargs)

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_object(session: Session, model: type[M], ident: Any, **kwargs: Any) -> dict:
    """Delete an object from the database.

    Parameters
    ----------
    session : Session
        The database session.
    model : type[SQLModel]
        The model to delete.
    ident : Any
        The identifier of the object to get.

    Returns
    -------
    dict
        {'ok': True}

    Raises
    ------
    HTTPException
        If the object doesn't exist.
    """
    db_obj = read_or_404(session, model, ident, **kwargs)
    session.delete(db_obj)
    session.commit()
    return {"ok": True}
