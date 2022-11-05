from fastapi import UploadFile
import typing as tp
from random import randint
import pathlib
import io
import shutil
import os   
from contextlib import contextmanager, asynccontextmanager
import aiofiles
from concurrent.futures import ProcessPoolExecutor
import asyncio

import matplotlib.pyplot as plt
import pydicom
from src.utils.tempfile import tempfile_context
from src.utils.crypto import generate_uuid
from .utils import (
    ExtensionsValidators,
    CustomZipFile
)

class MarkupLoader:
    def __init__(self, file: UploadFile) -> None:
        self._file = file
        
    async def load(self, path: pathlib.Path):
        async with aiofiles.open(path, 'wb') as f:
            await f.write(self._file.file.read())


class AsyncDicomListLoader:
    def __init__(self, files: tp.List[UploadFile]) -> None:
        self._files = files
    
    async def load(self, path: pathlib.Path) -> int:
        count = 0
        for file in self._files:
            if not ExtensionsValidators.is_dicom(file.filename):
                continue
    
            count += 1
            async with aiofiles.open(path.joinpath(f'{count}.dcm'), 'wb') as f:
                await f.write(file.file.read())
        return count
    

class AsyncArchiveLoader:
    def __init__(self, file: UploadFile) -> None:
        self._file = file
        
    async def load(self, path: pathlib.Path) -> int:
        with tempfile_context() as t_path:
            async with aiofiles.open(t_path, 'wb') as t_f:
                while True:
                    data = await self._file.read(1024*1024*5)
                    if not data: break
                    await t_f.write(data)
            
            zip_file = CustomZipFile(t_path)
            count = 0
            for file in zip_file.filelist:
                if not ExtensionsValidators.is_dicom(file.filename):
                    continue
                count += 1  
                zip_file.extract(member=file, path=path, parents=False, filename=f'{count}.dcm')
                await asyncio.sleep(0)
            
        return count


def dicom_to_image(path_to_dicom, path_to_save):
    ds = pydicom.dcmread(path_to_dicom)
    plt.imsave(path_to_save, ds.pixel_array, cmap=plt.bone())
    return path_to_save


class ResearchesStorage:
    _CAPTURES_FOLDER = 'captures'
    _MARKUP_FILENAME = 'markup.json'
    _PREVIEW_FILENAME = 'preview.jpg'
    
    def __init__(self, path: pathlib.Path) -> None:
        self._path = path
    
    def generate_preview(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        path = self._gen_path(foldername)
        
        captures_count = self.get_captures_count(foldername)
        capture_num = captures_count // 2
        capture_path = self.get_capture_path(foldername, capture_num)
        return dicom_to_image(capture_path, path.joinpath(self._PREVIEW_FILENAME))
        
    def get_captures_count(self, foldername: str) -> int:
        if not self.is_exists(foldername):
            return None
        
        path = self._gen_path(foldername)
        return len(os.listdir(path.joinpath(self._CAPTURES_FOLDER)))
    
    async def load_captures(self, foldername: str, files: tp.List[UploadFile]) -> tp.Optional[int]:
        if not self.is_exists(foldername):
            return None
        
        if len(files) == 1 and ExtensionsValidators.is_archive(files[0].filename):
            loader = AsyncArchiveLoader(files[0])
        else:
            loader = AsyncDicomListLoader(files)
        
        path = self._gen_path(foldername).joinpath(self._CAPTURES_FOLDER)
        loaded = await loader.load(path)
        if not loaded:
            return None
        return loaded  

    async def load_markup(self, foldername: str, file: UploadFile) -> tp.Optional[int]:
        if not self.is_exists(foldername) or not ExtensionsValidators.is_json:
            return None

        path = self._gen_path(foldername).joinpath(self._MARKUP_FILENAME)
        loader = MarkupLoader(file)
        await loader.load(path)
        return 1

    def create_empty_research(self, foldername: tp.Optional[str] = None) -> tp.Optional[str]:
        if foldername is None:
            foldername = self._gen_foldername()
            
        research_path = self._gen_path(foldername)
        research_path.mkdir(parents=True, exist_ok=True)
        
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        captures_path.mkdir()
        
        markup_path = research_path.joinpath(self._MARKUP_FILENAME)
        markup_path.touch()
        return foldername
    
    def remove_research(self, foldername: str) -> None:
        if not self.is_exists(foldername):
            return None
        
        research_path = self._gen_path(foldername)
        shutil.rmtree(research_path, ignore_errors=True)
    
    def get_preview_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self._gen_path(foldername)
        preview_path = research_path.joinpath(self._PREVIEW_FILENAME)
        return preview_path
        
    
    def get_capture_path(self, foldername: str, capture_num: int) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self._gen_path(foldername)
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        capture_path = captures_path.joinpath(f'{capture_num}.dcm')
        return capture_path
    
    def get_markup_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        if not self.is_exists(foldername):
            return None
        
        research_path = self._gen_path(foldername)
        markup_path = research_path.joinpath(self._MARKUP_FILENAME)
        return markup_path
    
    def is_exists(self, foldername: str) -> bool:
        research_path = self._gen_path(foldername)
        if research_path.exists():
            return True
        return False
    
    @staticmethod
    def _gen_foldername() -> str:
        return str(generate_uuid())

    def _gen_path(self, foldername: str) -> pathlib.Path:
        return pathlib.Path(self._path).joinpath(foldername[:2], foldername)

