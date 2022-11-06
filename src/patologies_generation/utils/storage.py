import typing as tp
import pathlib
import asyncio
import os

from fastapi import UploadFile

from src.utils.dicom import remove_patient_personal_data
from src.utils.storage import FileStorage
from src.utils.other import ExtensionsValidators
from src.utils.ct_loaders import (
    AsyncArchiveLoader,
    AsyncDicomListLoader
)


class TemporaryCTStorage(FileStorage):
    _CAPTURES_FOLDER = 'captures'
    
    def create_empty_ct(self, foldername: tp.Optional[str] = None) -> tp.Optional[str]:
        if foldername is None:
            foldername = self._gen_foldername()
            
        research_path = self.get_path_to_folder(foldername)
        research_path.mkdir(parents=True, exist_ok=True)
        
        captures_path = self.get_captures_path(foldername)
        captures_path.mkdir()
        return foldername
    
    
    async def load_captures(self, foldername: str, files: tp.List[UploadFile]) -> tp.Optional[int]:
        if not self.is_exists(foldername):
            return None
        
        if len(files) == 1 and ExtensionsValidators.is_archive(files[0].filename):
            loader = AsyncArchiveLoader(files[0])
        else:
            loader = AsyncDicomListLoader(files)
        
        path = self.get_path_to_folder(foldername).joinpath(self._CAPTURES_FOLDER)
        loaded = await loader.load(path)
        if not loaded:
            return None
        return loaded  

    def get_captures_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self.get_path_to_folder(foldername)
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        return captures_path
    
    async def depersonalize(self, foldername: str) -> None:
        if not self.is_exists(foldername):
            return None
        
        captures_count = self.get_captures_count(foldername)
        for i in range(1, captures_count+1):
            capture_path = self.get_capture_path(foldername, i)
            remove_patient_personal_data(capture_path)
            await asyncio.sleep(0)
            
    def get_captures_count(self, foldername: str) -> int:
        if not self.is_exists(foldername):
            return None
        
        path = self.get_path_to_folder(foldername)
        return len(os.listdir(path.joinpath(self._CAPTURES_FOLDER)))
    
    def get_capture_path(self, foldername: str, capture_num: int) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        captures_path = self.get_captures_path(foldername)
        capture_path = captures_path.joinpath(f'{capture_num}.dcm')
        if not capture_path.exists():
            return None
        return capture_path
