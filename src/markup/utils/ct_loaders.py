import typing as tp
import aiofiles
import pathlib
import asyncio

from fastapi import UploadFile

from src.utils.temp_file import tempfile_context
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
    
    
    