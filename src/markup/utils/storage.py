import typing as tp
import pathlib
import os   

from fastapi import UploadFile

from src.utils.dicom import dicom_to_image
from src.utils.storage import FileStorage
from .utils import ExtensionsValidators
from .ct_loaders import (
    MarkupLoader,
    AsyncArchiveLoader,
    AsyncDicomListLoader
)


class ResearchLoadersMixin:
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

    async def load_markup(self, foldername: str, file: UploadFile) -> tp.Optional[int]:
        if not self.is_exists(foldername) or not ExtensionsValidators.is_json:
            return None

        path = self.get_path_to_folder(foldername).joinpath(self._MARKUP_FILENAME)
        loader = MarkupLoader(file)
        await loader.load(path)
        return 1


class ResearchPathManagerMixin:
    def get_capture_path(self, foldername: str, capture_num: int) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self.get_path_to_folder(foldername)
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        capture_path = captures_path.joinpath(f'{capture_num}.dcm')
        return capture_path
    
    def get_preview_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self.get_path_to_folder(foldername)
        preview_path = research_path.joinpath(self._PREVIEW_FILENAME)
        if not preview_path.exists():
            self.generate_preview(foldername)
        return preview_path
        
    def get_markup_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self.get_path_to_folder(foldername)
        markup_path = research_path.joinpath(self._MARKUP_FILENAME)
        return markup_path


class ResearchesStorage(FileStorage, ResearchLoadersMixin, ResearchPathManagerMixin):
    _CAPTURES_FOLDER = 'captures'
    _MARKUP_FILENAME = 'markup.json'
    _PREVIEW_FILENAME = 'preview.jpg'
    
    def create_empty_research(self, foldername: tp.Optional[str] = None) -> tp.Optional[str]:
        if foldername is None:
            foldername = self._gen_foldername()
            
        research_path = self.get_path_to_folder(foldername)
        research_path.mkdir(parents=True, exist_ok=True)
        
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        captures_path.mkdir()
        
        markup_path = research_path.joinpath(self._MARKUP_FILENAME)
        markup_path.touch()
        
        preview_path = research_path.joinpath(self._PREVIEW_FILENAME)
        preview_path.touch()
        return foldername
    
    def remove_research(self, foldername: str) -> None:
        self.remove_folder(foldername)
    
    
    def generate_preview(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        path = self.get_path_to_folder(foldername)
        
        captures_count = self.get_captures_count(foldername)
        capture_num = captures_count // 2
        capture_path = self.get_capture_path(foldername, capture_num)
        return dicom_to_image(capture_path, path.joinpath(self._PREVIEW_FILENAME))
        
    def get_captures_count(self, foldername: str) -> int:
        if not self.is_exists(foldername):
            return None
        
        path = self.get_path_to_folder(foldername)
        return len(os.listdir(path.joinpath(self._CAPTURES_FOLDER)))

