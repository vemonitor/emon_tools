"""
DataPath Controller
"""
from sqlmodel import Session, select
from backend.core.deps import CurrentUser
from backend.models.db import DataPath


class DataPathController:
    """DataPath Controller"""
    @staticmethod
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

    @staticmethod
    def count_data_path(
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
        statement = select(DataPath)
        result = session.exec(statement).all()
        return len(result)
