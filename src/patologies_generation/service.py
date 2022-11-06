import typing as tp
import pathlib

from fastapi import UploadFile

from src import config
from src import exceptions as exc
from src.patologies_generation.utils.storage import TemporaryCTStorage
from src.patologies_generation import schemas as sch    


async def load(files: tp.List[UploadFile]):
    storage = TemporaryCTStorage(config.TEMPORARY_CT_STORAGE_PATH)
    foldername = storage.create_empty_ct()
    loaded = await storage.load_captures(foldername, files)

    if loaded is None:
        storage.remove_folder(foldername)
        raise exc.WRONG_FILES_FORMAT(error_description='you may load list of .dcm files or ONE archive with .dcm files')
    await storage.depersonalize(foldername)
    return foldername, loaded


def get_path_to_capture(id, capture_num) -> pathlib.Path:
    storage = TemporaryCTStorage(config.TEMPORARY_CT_STORAGE_PATH)
    path = storage.get_capture_path(id, capture_num)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research or capture was not found')
    return path
    
    
def get_params():
    types = [_type for _type in sch.Type]
    lobes = [lobe for lobe in sch.Lobe]
    lungs = [lung for lung in sch.Lung]
    counts = [count for count in sch.Count]
    sizes = [size for size in sch.SizeMm]
    return sch.GetParamsResponse(type=types,
                                 lobe=lobes,
                                 lung=lungs,
                                 count=counts,
                                 size_mm=sizes)
    
    
def generate_patologies(body: sch.GeneratePatologiesRequest):
    pass
    
    
    
    
    
    
    
    
    
    
    