from fastapi import UploadFile
import typing as tp
import pathlib
import io
import shutil
import os   
from contextlib import contextmanager, asynccontextmanager
import aiofiles
from concurrent.futures import ProcessPoolExecutor
import asyncio

from src.utils.tempfile import tempfile_context
from src.utils.crypto import generate_uuid
from .utils import (
    ExtensionsValidators,
    CustomZipFile
)


# class MarkupLoader:
#     def __init__(self, file: UploadFile) -> None:
#         self._file = file
        
#     def load(self, path: pathlib.Path):
#         with open(path.joinpath(f'{i+1}.dcm'), 'xb') as f:
#             f.write(self._file.file.read())
    
#     def validate(self) -> bool:
#         return ExtensionsValidators.is_json(self._file.filename)


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

class ResearchesStorage:
    _CAPTURES_FOLDER = 'captures'
    _MARKUP_FILENAME = 'markup.json'
    
    def __init__(self, path: pathlib.Path) -> None:
        self._path = path
    
    async def load_captures(self, foldername: str, files: tp.List[UploadFile]) -> int:
        if len(files) == 1 and ExtensionsValidators.is_archive(files[0].filename):
            loader = AsyncArchiveLoader(files[0])
        else:
            loader = AsyncDicomListLoader(files)
        
        path = self._gen_path(foldername).joinpath(self._CAPTURES_FOLDER)
        return await loader.load(path)  

    def load_markup(self, foldername: str, file: UploadFile):
        # FileLoader.load(...)
        pass

    def create_empty_research(self, foldername: tp.Optional[str] = None):
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
        research_path = self._gen_path(foldername)
        shutil.rmtree(research_path, ignore_errors=True)
    
    def get_capture_path(self, foldername: str, capture_num: int) -> tp.Optional[pathlib.Path]:
        research_path = self._gen_path(foldername)
        captures_path = research_path.joinpath(self._CAPTURES_FOLDER)
        capture_path = captures_path.joinpath(f'{capture_num}.dcm')
        if capture_path.exists():
            return capture_path
        return None
    
    def get_markup_path(self, foldername: str) -> tp.Optional[pathlib.Path]:
        research_path = self._gen_path(foldername)
        markup_path = research_path.joinpath(self._MARKUP_FILENAME)
        if markup_path.exists():
            return markup_path
        return None
    
    @staticmethod
    def _gen_foldername() -> str:
        return str(generate_uuid())

    def _gen_path(self, foldername: str) -> pathlib.Path:
        return pathlib.Path(self._path).joinpath(foldername[:2], foldername)

