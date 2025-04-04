"""
Emon Api Routes
"""
from fastapi import APIRouter
from emon_tools.emon_api.api_utils import Utils as Ut
from backend.api.deps import CurrentUser, SessionDep
from backend.controllers.base import BaseController
from backend.controllers.emon_api import EmonApiController
from backend.controllers.emon_host import EmonHostController
from backend.models.emon_api import EmonFeeds, FeedDataPoints, GetFeedDataModel

router = APIRouter(prefix="/emoncms", tags=["emoncms"])
# pylint: disable=broad-exception-caught


@router.get(
    "/feeds/{host_slug}/",
    response_model=EmonFeeds,
    responses=BaseController.get_error_responses()
)
async def get_feeds(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    host_slug: str
) -> dict:
    """Test if if is valid source directory."""
    try:
        host = EmonHostController.get_emon_host_by_slug(
            session=session,
            current_user=current_user,
            slug=host_slug
        )
        if not host:
            return EmonFeeds(
                success=False
            )
        api_feeds = EmonApiController.get_host_feed_list(
            host=host
        )

        feeds = EmonApiController.get_host_feeds(
            session=session,
            current_user=current_user,
            host_id=host.id,
            feeds=api_feeds
        )
        return EmonFeeds(
            success=True,
            host_id=host.id,
            nb_feeds=len(feeds),
            feeds=feeds
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/data/{host_slug}/{feed_id}/",
    response_model=FeedDataPoints,
    responses=BaseController.get_error_responses()
)
async def get_feed_data(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    host_slug: str,
    feed_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> FeedDataPoints:
    """Test if if is valid source directory."""
    try:
        GetFeedDataModel(
            host_slug=host_slug,
            feed_id=feed_id,
            start=start,
            interval=interval,
            window=window
        )
        host = EmonHostController.get_emon_host_by_slug(
            session=session,
            current_user=current_user,
            slug=host_slug
        )
        if not host:
            return FeedDataPoints(
                success=False
            )
        data = EmonApiController.get_host_feed_data(
            host=host,
            feed_id=feed_id,
            start=start,
            window=window,
            interval=interval
        )
        if Ut.is_dict(data)\
                and data.get('success') is True\
                and Ut.is_list(data.get('message'), not_empty=True):
            return FeedDataPoints(
                success=True,
                id=feed_id,
                name=f"{feed_id}",
                data=data.get('message')
            )
        return FeedDataPoints(
                success=False
            )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
