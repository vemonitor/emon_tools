"""
Sql Model Crud
"""
import uuid
from typing import Any

from sqlmodel import Session, select

from emon_tools.fastapi.core.security import get_password_hash, verify_password
from emon_tools.fastapi.models.db import EmonHost, EmonHostCreate
from emon_tools.fastapi.models.db import User
from emon_tools.fastapi.models.db import UserCreate
from emon_tools.fastapi.models.db import UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        session (Session):
            The database session to use for the operation.
        user_create (UserCreate):
            An object containing the details of the user to be created.

    Returns:
        User: The newly created user object.

    Raises:
        SQLAlchemyError: If there is an error during the database operation.
    """
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(
            user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(
    *,
    session: Session,
    db_user: User,
    user_in: UserUpdate
) -> Any:
    """
    Update an existing user in the database.

    Args:
        session (Session): The database session to use for the update.
        db_user (User): The existing user object to be updated.
        user_in (UserUpdate): The new data for the user.

    Returns:
        Any: The updated user object.

    Notes:
        - If the `user_in` contains a password, it will be hashed
          and stored in the `hashed_password` field.
        - The function commits the changes to the database
          and refreshes the `db_user` object.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(*, session: Session, user_id: uuid.uuid4) -> User | None:
    """
    Retrieve a user from the database by their email address.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    statement = select(User).where(User.id == user_id)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Retrieve a user from the database by their email address.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(
    *,
    session: Session,
    email: str,
    password: str
) -> User | None:
    """
    Authenticate a user by their email and password.

    Args:
        session (Session): The database session to use for querying.
        email (str): The email address of the user.
        password (str): The plain text password of the user.

    Returns:
        User | None: The authenticated user object
        if authentication is successful, otherwise None.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_emon_host(
    *,
    session: Session,
    item_in: EmonHostCreate,
    owner_id: uuid.UUID
) -> EmonHost:
    """
    Create a new EmonHost in the database.

    Args:
        session (Session): The database session to use for the operation.
        item_in (EmonHostCreate): The data required to create a new item.
        owner_id (uuid.UUID): The UUID of the owner of the item.

    Returns:
        EmonHost: The newly created item.
    """
    db_item = EmonHost.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
