"""
EmonApi Controller
"""
from typing import Optional
from sqlmodel import Session, select
from backend.models.emon_api import ApiFeedItem, ApiFeeds, EmonFeedItem
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.emon_api.emon_api import EmonFeedsApi
from backend.controllers.files import FilesController
from backend.core.deps import CurrentUser
from backend.models.db import EmonHost


class EmonApiController:
    """EmonApi Controller"""
    @staticmethod
    def format_api_feed(
        feed: ApiFeedItem
    ) -> Optional[EmonFeedItem]:
        """Format api feed item"""
        interval = int(feed.get('interval', 0))
        size = int(feed.get('size', 0))
        if size == 0\
                or feed.get('start_time', 0) == 0\
                or feed.get('end_time', 0) == 0\
                or interval == 0:
            return None
        meta = {
            'start_time': feed.get('start_time'),
            'end_time': feed.get('end_time'),
            'interval': 0,
            'npoints': 0,
            'size': 0,
        }
        if interval > 0:
            meta.update({
                'start_time': feed.get('start_time', 0),
                'end_time': feed.get('end_time', 0),
                'interval': interval,
                'npoints': 0,
                'size': size,
            })
        return {
            'id': int(feed.get('id')),
            'userid': int(feed.get('userid')),
            'name': feed.get('name'),
            'tag': feed.get('tag'),
            'public': feed.get('public') == '1',
            'engine': feed.get('engine'),
            'unit': feed.get('unit'),
            'meta': meta,
            'files': []
        }

    @staticmethod
    def get_host_feeds(
        *,
        session: Session,
        current_user: CurrentUser,
        host_id: int,
        feeds: ApiFeeds
    ) -> EmonHost | None:
        """
        Count DataPaths present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of DataPaths in data base
        """
        files = FilesController.get_files_by_host(
            session=session,
            current_user=current_user,
            host_id=host_id
        )
        result = None
        if Ut.is_dict(feeds, not_empty=True)\
                and feeds.get('success') is True\
                and Ut.is_list(feeds.get('message'), not_empty=True):
            has_files = Ut.is_list(files, not_empty=True)
            result = []
            for feed in feeds.get('message'):
                item = EmonApiController.format_api_feed(feed)
                if item is None:
                    continue
                if has_files:
                    for file in files:
                        if file.feed_id == feed.get('id'):
                            item['files'].append(file)
                result.append(item)
        return result

    @staticmethod
    def get_host_feed_list(
        host: EmonHost
    ) -> Optional[ApiFeeds]:
        """
        Count DataPaths present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of DataPaths in data base
        """
        api = EmonFeedsApi(
            url=host.host,
            api_key=host.api_key
        )
        return api.list_feeds()

    @staticmethod
    def get_host_feed_data(
        host: EmonHost,
        feed_id: int,
        start: int = 0,
        interval: int = 0,
        window: int = 0
    ) -> Optional[ApiFeeds]:
        """
        Count DataPaths present.

        Args:
            session (Session): The database session to use for the query.

        Returns:
            int: Number of DataPaths in data base
        """
        api = EmonFeedsApi(
            url=host.host,
            api_key=host.api_key
        )
        return api.get_fetch_feed_data(
            feed_id=feed_id,
            start=start,
            end=start + window,
            interval=interval
        )

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
