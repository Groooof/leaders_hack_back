from pprint import pprint
import typing as tp
import uuid
import asyncpg
from fastapi import APIRouter, Depends, UploadFile, Form
from fastapi.responses import FileResponse

from src import config
from src.auth import backends
from src.auth.utils import JWTToken
from src.dependencies import get_db_connection
from src.schemas import Error
from src.markup.utils import ResearchesStorage
from src.markup.crud import crud
from src.markup import service
import src.markup.schemas as sch
import src.exceptions as exc


router = APIRouter(prefix='/api/v1', tags=['markup'])
router.responses = {403: {'description': 'Access denied', 'model': Error},
                    401: {'description': 'Token expired', 'model': Error}}


@router.post('/research',
             dependencies=[Depends(backends.jwt_auth),
                           Depends(backends.is_moderator)])
async def create_research(files: tp.List[UploadFile],
                          name: str = Form(),
                          description: str = Form(),
                          tags: tp.List[str] = Form(default=None), 
                          con: asyncpg.Connection = Depends(get_db_connection),
                          jwt: JWTToken = Depends(backends.get_token)):
    
    tags = ''.join(tags).split(',') if tags is not None else []
    research_id = await service.create_research(con, jwt.user, name, description, tags)
    loaded = await service.load_captures(research_id, files)
    return sch.CreateResearchResponse(research_id=research_id, captures_count=loaded)


@router.get('/research/{research_id}/preview', dependencies=[Depends(backends.jwt_auth)])
async def get_preview(research_id: str):
    path = service.get_path_to_preview(research_id)
    return FileResponse(path)


@router.get('/research/{research_id}/captures/{capture_num}', dependencies=[Depends(backends.jwt_auth)])
async def get_capture(research_id: str, capture_num: int):
    
    path = service.get_path_to_capture(research_id, capture_num)
    return FileResponse(path)


@router.get('/research/{research_id}/markup', dependencies=[Depends(backends.jwt_auth)])
async def get_markup(research_id: str, 
                     con: asyncpg.Connection = Depends(get_db_connection),
                     jwt: JWTToken = Depends(backends.get_token)):
    
    path = service.get_path_to_markup(research_id)
    await service.check_access_to_research(con, jwt.user, research_id)
    return FileResponse(path)


@router.post('/research/{research_id}/markup', dependencies=[Depends(backends.jwt_auth)])
async def upload_markup(research_id: str, 
                        file: UploadFile,
                        con: asyncpg.Connection = Depends(get_db_connection),
                        jwt: JWTToken = Depends(backends.get_token)):

    await service.check_access_to_research(con, jwt.user, research_id)
    await service.upload_markup(research_id, file)
    
    
@router.get('/research/markers', dependencies=[Depends(backends.jwt_auth),
                                               Depends(backends.is_moderator)])
async def get_markers(con: asyncpg.Connection = Depends(get_db_connection)):
    return await service.get_markers(con)


@router.get('/research/search/tags', dependencies=[Depends(backends.jwt_auth)])
async def get_tags(con: asyncpg.Connection = Depends(get_db_connection)):
    return await service.get_tags(con)


@router.post('/research/search/tags', dependencies=[Depends(backends.jwt_auth),
                                                    Depends(backends.is_moderator)])
async def add_tags(body: sch.AddTagsRequest, con: asyncpg.Connection = Depends(get_db_connection)):
    await service.add_tags(con, body.tags)


@router.post('/research/{task_id}/status', dependencies=[Depends(backends.jwt_auth),
                                                        Depends(backends.is_moderator)])
async def change_task_status(task_id: int,
                             body: sch.ChangeTaskStatusRequest,
                             con: asyncpg.Connection = Depends(get_db_connection),
                             jwt: JWTToken = Depends(backends.get_token)):
    
    # await service.check_access_to_research(con, jwt.user, research_id)
    await service.change_task_status(con, task_id, body.status)


@router.post('/task', dependencies=[Depends(backends.jwt_auth),
                                    Depends(backends.is_moderator)])
async def create_task(body: sch.CreateTaskRequest, con: asyncpg.Connection = Depends(get_db_connection)):
    return await service.create_task(con, body.research_id, body.user_id, body.deadline)


@router.post('/research/search', dependencies=[Depends(backends.jwt_auth),
                                               Depends(backends.is_moderator)])
async def search_researches(body: tp.Optional[sch.SearchResearchesRequest] = None, 
                 con: asyncpg.Connection = Depends(get_db_connection),
                 jwt: JWTToken = Depends(backends.get_token)):
    return await service.search_researches(con, body)


@router.post('/tasks/search', dependencies=[Depends(backends.jwt_auth)])
async def search_tasks(body: tp.Optional[sch.SearchTasksRequest] = None, 
                       con: asyncpg.Connection = Depends(get_db_connection),
                       jwt: JWTToken = Depends(backends.get_token)):
        
    if jwt.role == 'marker':
        body.user_id = jwt.id
    return await service.search_tasks(con, body)


@router.post('/test')
async def test(con: asyncpg.Connection = Depends(get_db_connection)):
    await crud.search(con, None, None, None)


