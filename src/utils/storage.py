import typing as tp
import pathlib
import shutil
from functools import lru_cache
from .crypto import generate_uuid


class FileStorage:
    def __init__(self, root_path: pathlib.Path) -> None:
        self._root = root_path

    def create_folder(self, foldername) -> pathlib.Path:
        if foldername is None:
            foldername = self._gen_foldername()
            
        path_to_folder = self.get_path_to_folder(foldername)
        path_to_folder.mkdir(parents=True, exist_ok=True)
        return path_to_folder
    
    def remove_folder(self, foldername) -> None:
        if not self.is_exists(foldername):
            return None
        research_path = self.get_path_to_folder(foldername)
        shutil.rmtree(research_path, ignore_errors=True)
    
    @lru_cache(maxsize=256)
    def get_path_to_folder(self, foldername) -> tp.Optional[pathlib.Path]:
        return pathlib.Path(self._root).joinpath(foldername[:2], foldername)

    def is_exists(self, foldername: str) -> bool:
        path_to_folder = self.get_path_to_folder(foldername)
        if path_to_folder.exists():
            return True
        return False

    @staticmethod
    def _gen_foldername() -> str:
        return str(generate_uuid())