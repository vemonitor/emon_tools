"""
Sql Model Crud
"""
import uuid
from typing import Any
import datetime as dt
from slugify import slugify
from sqlmodel import Session, select
from sqlmodel import col
from sqlalchemy.exc import IntegrityError
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.fastapi.core.deps import CurrentUser
from emon_tools.fastapi.core.security import get_password_hash, verify_password
from emon_tools.fastapi.models.db import ArchiveFile, DataPath, EmonHost, EmonHostCreate
from emon_tools.fastapi.models.db import User
from emon_tools.fastapi.models.db import UserCreate
from emon_tools.fastapi.models.db import UserUpdate
from emon_tools.fastapi.utils.emon_fina_helper import EmonFinaHelper
from emon_tools.fastapi.utils.errors_parser import parse_integrity_error


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


def get_data_path(
    *,
    session: Session,
    current_user: CurrentUser,
    item_id: int
) -> DataPath | None:
    """
    Retrieve a data path from the database by their id.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    statement = select(DataPath).where(DataPath.id == item_id)
    if not current_user.is_superuser:
        statement.where(DataPath.owner_id == current_user.id)
    result = session.exec(statement).first()
    return result


def get_file_item(
    *,
    session: Session,
    current_user: CurrentUser,
    item_id: int
) -> ArchiveFile | None:
    """
    Retrieve a data path from the database by their id.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    statement = select(ArchiveFile).where(ArchiveFile.id == item_id)
    if not current_user.is_superuser:
        statement.where(ArchiveFile.owner_id == current_user.id)
    result = session.exec(statement).first()
    return result


def get_archive_file_by_names(
    *,
    session: Session,
    current_user: CurrentUser,
    file_names: list[str]
) -> DataPath | None:
    """
    Retrieve a data path from the database by their id.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    statement = select(ArchiveFile).where(
        col(ArchiveFile.file_name).in_(file_names)
    )
    if not current_user.is_superuser:
        statement.where(DataPath.owner_id == current_user.id)
    session_res = session.exec(statement).all()
    return session_res


def register_files(
    *,
    session: Session,
    current_user: CurrentUser,
    files: list[dict]
) -> DataPath | None:
    """
    Retrieve a data path from the database by their id.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = 0
    if Ut.is_dict(files)\
            and Ut.is_list(files.get('files'), not_empty=True):
        to_add = [
            x
            for x in files.get('files')
            if x.get('file_db') is None
        ]
        if len(to_add) > 0:
            owner_id = current_user.id
            for item in to_add:
                item_in = ArchiveFile(
                    name=item.get('file_name'),
                    slug=slugify(item.get('file_name')),
                    file_name=item.get('file_name'),
                    datapath_id=files.get('file_path').id,
                    owner_id=owner_id,
                    start_time=dt.datetime.fromtimestamp(
                        item['meta'].get('start_time'),
                        dt.timezone.utc),
                    end_time=dt.datetime.fromtimestamp(
                        item['meta'].get('end_time'),
                        dt.timezone.utc),
                    interval=item['meta'].get('interval'),
                    npoints=item['meta'].get('npoints'),
                    size=item['meta'].get('size'),
                )
                session.add(item_in)
                result += 1
            session.commit()
    return result


def get_files_from_data_path(
    *,
    session: Session,
    current_user: CurrentUser,
    item_id: int
) -> dict:
    """
    Retrieve a data path from the database by their id.

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = {
        "succes": False
    }
    current = get_data_path(
        session=session,
        current_user=current_user,
        item_id=item_id
    )
    files = EmonFinaHelper.scan_fina_dir(
        file_path=current.path
    )
    try:
        if Ut.is_set(
                files.get('file_names'), not_empty=True):
            db_files = get_archive_file_by_names(
                session=session,
                current_user=current_user,
                file_names=list(files.get('file_names'))
            )
            if Ut.is_list(db_files, not_empty=True):
                outputs = []
                for item in files.get('files'):
                    db_item = [
                        x
                        for x in db_files
                        if x.file_name == item.get('file_name')
                    ]
                    if len(db_item) > 0:
                        db_item = db_item[0]
                        item.update({
                            'file_db': {
                                'file_id': db_item.id,
                                'name': db_item.name,
                                'slug': db_item.slug,
                                'feed_id': db_item.feed_id,
                                'emonhost_id': db_item.emonhost_id,
                            }    
                        })
                    outputs.append(item)
                files['files'] = outputs
            files['file_path'] = current
            return files
    except IntegrityError as ex:
        result['msg'] = "Unable to get archived files list from data base."
        result['error'] = parse_integrity_error(ex)

    return result
