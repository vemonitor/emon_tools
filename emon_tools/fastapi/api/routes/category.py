"""Category api routes."""
from typing import Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlmodel import func
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from emon_tools.fastapi.api.deps import CurrentUser, SessionDep
from emon_tools.fastapi.models.db import Category
from emon_tools.fastapi.models.db import CategoryCreate
from emon_tools.fastapi.models.db import CategoryUpdate
from emon_tools.fastapi.models.db import CategorysPublic
from emon_tools.fastapi.models.base import ResponseModelBase
from emon_tools.fastapi.utils.errors_parser import parse_integrity_error
from emon_tools.fastapi.utils.errors_parser import parse_pydantic_errors
# pylint: disable=not-callable
router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=CategorysPublic)
async def read_root(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> dict:
    """Retrieve category list."""
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Category)
        count = session.exec(count_statement).one()
        statement = select(Category).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Category)
            .where(Category.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Category)
            .where(Category.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    return CategorysPublic(data=items, count=count)


@router.get("/get/{item_id}/", response_model=ResponseModelBase)
def read_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int
) -> Any:
    """
    Get item by ID.
    """
    try:
        item = session.get(Category, item_id)
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
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.post("/add/", response_model=ResponseModelBase)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: CategoryCreate
) -> Any:
    """
    Create new item.
    """
    try:
        item = Category.model_validate(
            item_in, update={"owner_id": current_user.id}
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return ResponseModelBase(
            success=True,
            data=dict(item)
        )
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.put("/edit/{item_id}/", response_model=ResponseModelBase)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int,
    item_in: CategoryUpdate,
) -> Any:
    """
    Update an item.
    """
    try:
        item = session.get(Category, item_id)
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
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.delete("/delete/{item_id}/", response_model=ResponseModelBase)
def delete_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int
) -> ResponseModelBase:
    """
    Delete an item.
    """
    try:
        item = session.get(Category, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        session.delete(item)
        session.commit()
        return ResponseModelBase(
            success=True,
            msg="Category deleted successfully"
        )
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex
