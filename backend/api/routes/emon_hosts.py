"""EmonHost api routes."""
from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sqlmodel import func

from backend.api.deps import CurrentUser, SessionDep
from backend.controllers.base import BaseController
from backend.controllers.emon_host import EmonHostController
from backend.models.base import (
    ResponseMessage,
    ResponseModelBase
)
from backend.models.db import (
    EmonHost,
    EmonHostCreate,
    EmonHostUpdate,
    EmonHostsPublic,
)

router = APIRouter(prefix="/emon_host", tags=["emon_host"])
# pylint: disable=broad-exception-caught, not-callable


@router.get(
    "/",
    response_model=EmonHostsPublic,
    responses=BaseController.get_error_responses()
)
async def read_root(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> dict:
    """Retrieve emon_hosts list."""
    try:
        if current_user.is_superuser:
            count_statement = select(func.count()).select_from(EmonHost)
            count = session.exec(count_statement).one()
            statement = select(EmonHost).offset(skip).limit(limit)
            items = session.exec(statement).all()
        else:
            count_statement = (
                select(func.count())
                .select_from(EmonHost)
                .where(EmonHost.owner_id == current_user.id)
            )
            count = session.exec(count_statement).one()
            statement = (
                select(EmonHost)
                .where(EmonHost.owner_id == current_user.id)
                .offset(skip)
                .limit(limit)
            )
            items = session.exec(statement).all()

        return EmonHostsPublic(data=items, count=count)
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/get/{item_id}/",
    response_model=ResponseModelBase,
    responses=BaseController.get_error_responses()
)
def read_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int
) -> Any:
    """
    Get item by ID.
    """
    try:
        item = session.get(EmonHost, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        return ResponseModelBase(
            success=True,
            data=dict(item)
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/by/{item_slug}/",
    response_model=ResponseModelBase,
    responses=BaseController.get_error_responses()
)
def read_item_by_slug(
    session: SessionDep,
    current_user: CurrentUser,
    item_slug: str
) -> Any:
    """
    Get item by ID.
    """
    try:
        item = EmonHostController.get_emon_host_by_slug(
            session=session,
            current_user=current_user,
            slug=item_slug
        )
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        return ResponseModelBase(
            success=True,
            data=dict(item)
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.post(
    "/add/",
    response_model=ResponseModelBase,
    responses=BaseController.get_error_responses()
)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: EmonHostCreate
) -> ResponseModelBase:
    """
    Create new item.
    """
    try:
        item = EmonHost.model_validate(
            item_in, update={"owner_id": current_user.id})
        session.add(item)
        session.commit()
        session.refresh(item)
        return ResponseModelBase(
            success=True,
            data=dict(item)
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.put(
    "/edit/{item_id}/",
    response_model=ResponseModelBase,
    responses=BaseController.get_error_responses()
)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int,
    item_in: EmonHostUpdate,
) -> ResponseModelBase:
    """
    Update an item.
    """
    try:
        item = session.get(EmonHost, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        session.add(item)
        session.commit()
        session.refresh(item)
        return ResponseModelBase(
            success=True,
            data=dict(item)
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.delete(
    "/delete/{item_id}/",
    response_model=ResponseMessage,
    responses=BaseController.get_error_responses()
)
def delete_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int
) -> ResponseMessage:
    """
    Delete an item.
    """
    try:
        item = session.get(EmonHost, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        session.delete(item)
        session.commit()
        return ResponseMessage(
            success=True,
            msg="Emon Host deleted successfully"
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
