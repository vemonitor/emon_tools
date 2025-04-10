"""
EmonHost Controller
"""
import uuid
from sqlmodel import Session, select
from backend.core.deps import CurrentUser
from backend.models.db import EmonHost
from backend.models.db import EmonHostCreate


class EmonHostController:
    """EmonHost Controller"""
    @staticmethod
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
        db_item = EmonHost.model_validate(
            item_in, update={"owner_id": owner_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @staticmethod
    def get_emon_host_by_slug(
        *,
        session: Session,
        current_user: CurrentUser,
        slug: str
    ) -> EmonHost | None:
        """
        Count DataPaths present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of DataPaths in data base
        """
        statement = select(EmonHost).where(EmonHost.slug == slug)
        if not current_user.is_superuser:
            statement.where(EmonHost.owner_id == current_user.id)
        result = session.exec(statement).first()
        return result

    @staticmethod
    def count_emon_hosts(
        *,
        session: Session
    ) -> int:
        """
        Count DataPaths present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of DataPaths in data base
        """
        statement = select(EmonHost)
        result = session.exec(statement).all()
        return len(result)
