"""
DataPath Controller
"""
import datetime as dt
from typing import Any, Dict
from slugify import slugify
from sqlmodel import Session, select
from sqlmodel import col, func
from sqlalchemy.exc import IntegrityError
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.fastapi.controllers.data_path import DataPathController
from emon_tools.fastapi.core.deps import CurrentUser
from emon_tools.fastapi.models.db import ArchiveFile
from emon_tools.fastapi.models.db import DataPath
from emon_tools.fastapi.utils.emon_fina_helper import EmonFinaHelper
from emon_tools.fastapi.utils.errors_parser import parse_integrity_error
# pylint: disable=not-callable, no-member


class FilesController:
    """DataPath Controller"""
    @staticmethod
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

    @staticmethod
    def count_files(
        *,
        session: Session
    ) -> int:
        """
        Count users present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of users in data base
        """
        statement = select(ArchiveFile.id)
        result = session.exec(statement).all()
        return len(result)

    @staticmethod
    def count_files_by_types(
        *,
        session: Session
    ) -> Dict[Any, Dict[Any, int]]:
        """
        Count users present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of users in data base
        """
        statement = (
            select(
                DataPath.path_type,
                DataPath.file_type,
                func.count(func.distinct(ArchiveFile.id))
            )
            .join(DataPath, ArchiveFile.datapath_id == DataPath.id)
            .group_by(DataPath.path_type, DataPath.file_type)
        )
        results = session.exec(statement).all()
        counts: Dict[Any, Dict[Any, int]] = {}
        for path_type, file_type, count in results:
            if path_type not in counts:
                counts[path_type.value] = {}
            counts[path_type.value][file_type.value] = count

        return counts

    @staticmethod
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

    @staticmethod
    def sum_archive_file_sizes_by_types(
        *,
        session: Session
    ) -> Dict[Any, Dict[Any, int]]:
        """
        Sum ArchiveFile sizes grouped by DataPath.path_type
        and DataPath.file_type.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            Dict[Any, Dict[Any, int]]:
                A nested dictionary where each outer key is
                a DataPath.path_type, and each inner key is
                a DataPath.file_type mapping to the sum
                of ArchiveFile.size.
        """
        statement = (
            select(
                DataPath.path_type,
                DataPath.file_type,
                func.sum(ArchiveFile.size)
            )
            .join(DataPath, ArchiveFile.datapath_id == DataPath.id)
            .group_by(DataPath.path_type, DataPath.file_type)
        )
        results = session.exec(statement).all()

        size_sums: Dict[Any, Dict[Any, int]] = {}
        for path_type, file_type, total_size in results:
            if path_type not in size_sums:
                size_sums[path_type] = {}
            # Use 0 as fallback if total_size is None
            size_sums[path_type][file_type] = total_size or 0

        return size_sums

    @staticmethod
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

    @staticmethod
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
        current = DataPathController.get_data_path(
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
                db_files = FilesController.get_archive_file_by_names(
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
