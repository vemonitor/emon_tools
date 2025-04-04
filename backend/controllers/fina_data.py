"""Fina Data Controller"""


from backend.controllers.files import FilesController
from backend.core.deps import CurrentUser, SessionDep
from backend.utils.emon_fina_helper import EmonFinaHelper


class FinaDataController:
    """Fina Data Controller"""
    @staticmethod
    def get_files_list(
        session: SessionDep,
        current_user: CurrentUser,
        path_id: int
    ) -> list:
        """Get phpfina files list from source."""
        files = FilesController.get_files_from_data_path(
                session=session,
                current_user=current_user,
                item_id=path_id
            )
        output_files = EmonFinaHelper.append_fina_data(
            files=files
        )
        nb_added = FilesController.register_files(
            session=session,
            current_user=current_user,
            files=output_files
        )
        return output_files, nb_added
