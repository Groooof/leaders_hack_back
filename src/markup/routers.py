import asyncpg
import typing as tp
from timeit import default_timer
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks

from src import config
from src.auth import backends
from src.auth.utils import JWTToken
from src.dependencies import get_db_connection
from src.markup import crud
from src.schemas import Error
from src.markup.utils import ResearchesStorage
from src.markup.crud import crud
import src.markup.schemas as sch
import src.exceptions as exc


router = APIRouter(prefix='/api/v1', tags=['markup'])
router.responses = {403: {'description': 'Access denied', 'model': Error},
                    401: {'description': 'Token expired', 'model': Error}}


@router.post('/research',)
             #dependencies=[Depends(backends.check_signature),])
                           #Depends(backends.is_moderator)])
async def create_research(background_tasks: BackgroundTasks,
                          files: tp.List[UploadFile], 
                          con: asyncpg.Connection = Depends(get_db_connection)):
                          #jwt: JWTToken = Depends(backends.get_token)):
    
    storage = ResearchesStorage(config.RESEARCHES_PATH)
    research_id = storage.create_empty_research()
    loaded = await storage.load_captures(research_id, files)
    
    if not loaded:
        storage.remove_research(research_id)
        raise exc.WRONG_FILES_FORMAT(error_description='you may load list of .dcm files or ONE archive with .dcm files')
    return sch.CreateResearchResponse(research_id=research_id, captures_count=loaded)


@router.get('/research/{research_id}/captures/{capture_num}')
async def get_capture(research_id: str, capture_num: int):
    storage = ResearchesStorage(config.RESEARCHES_PATH)
    path = storage.get_capture_path(research_id, capture_num)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research or capture was not found')
    return FileResponse(path)


@router.get('/research/{research_id}/markup',
            dependencies=[Depends(backends.check_signature)])
async def get_markup(research_id: str, 
                     con: asyncpg.Connection = Depends(get_db_connection),
                     jwt: JWTToken = Depends(backends.get_token)):
    
    storage = ResearchesStorage(config.RESEARCHES_PATH)
    path = storage.get_markup_path(research_id)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research was not found')
    
    have_access = await crud.have_access_to_markup(con, jwt.user, research_id)
    if not have_access:
        raise exc.ACCESS_DENIED(error_description='you have not acces to this markup (only creator and markers)')

    return FileResponse(path)


@router.get('/get_admin')#, dependencies=[Depends(backends.jwt_auth),
                          #              Depends(backends.is_superuser)])
async def get_admin(con: asyncpg.Connection = Depends(get_db_connection)):

    return {'Hello': 1}

    
    


