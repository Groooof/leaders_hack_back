import typing as tp 

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from src.auth import backends
from src.schemas import Error
from src import exceptions as exc
from src.patologies_generation import service
from src.patologies_generation import schemas as sch


router = APIRouter(prefix='/api/v1', tags=['generation'])
router.responses = {403: {'description': 'Access denied', 'model': Error},
                    401: {'description': 'Token expired', 'model': Error},
                    400: {'description': 'Invalid request data', 'model': Error}}

@router.post('/generation/load', dependencies=[Depends(backends.jwt_auth)], response_model=sch.LoadResponse)
async def load(files: tp.List[UploadFile]):
    foldername, loaded = await service.load(files)    
    return sch.LoadResponse(loaded=loaded, id=foldername)


@router.get('/generation/{id}/captures/{capture_num}')#, dependencies=[Depends(backends.jwt_auth)])
async def get_capture(id: str, capture_num: int):
    
    path = service.get_path_to_capture(id, capture_num)
    return FileResponse(path)


@router.get('/generation/params', dependencies=[Depends(backends.jwt_auth)], response_model=sch.GetParamsResponse)
async def get_params():
    return service.get_params()


@router.post('/generation/{id}/captures/{capture_num}/generate', dependencies=[Depends(backends.jwt_auth)])
async def generate_patologies(body: sch.GeneratePatologiesRequest):
    capture_with_patologies = service.generate_patologies(body)
    return FileResponse()

