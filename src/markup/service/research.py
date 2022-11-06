import datetime as dt
import typing as tp
import pathlib

import asyncpg
from fastapi import UploadFile

from src import exceptions as exc
from src import config
from src.markup import crud
from src.markup import utils
from src.markup import schemas as sch   


async def create_research(con: asyncpg.Connection, creator_id: str, name: str, description: str, tags: tp.List[str]) -> str:
    research_id = await crud.create_research(con, creator_id, name, description, tags)
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    storage.create_empty_research(research_id)
    return research_id


async def create_task(con: asyncpg.Connection, research_id: str, user_id: int, deadline: dt.datetime):
    res = await crud.create_task(con, research_id, user_id, deadline)
    return sch.CreateTaskResponse(id=res['id'],
                                  created_at=res['created_at'],
                                  status=res['status'])


async def load_captures(research_id: str, files: tp.List[UploadFile]) -> int:
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    loaded = await storage.load_captures(research_id, files)
    
    if loaded is None:
        storage.remove_research(research_id)
        raise exc.WRONG_FILES_FORMAT(error_description='you may load list of .dcm files or ONE archive with .dcm files')
    storage.generate_preview(research_id)
    await storage.depersonalize(research_id)
    return loaded


def get_path_to_capture(research_id: str, capture_num: int) -> tp.Union[str, pathlib.Path]:
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    path = storage.get_capture_path(research_id, capture_num)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research or capture was not found')
    return path


def get_path_to_markup(research_id: str) -> tp.Union[str, pathlib.Path]:
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    path = storage.get_markup_path(research_id)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research was not found')
    return path


def get_path_to_preview(research_id: str) -> tp.Union[str, pathlib.Path]:
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    path = storage.get_preview_path(research_id)
    if path is None:
        raise exc.FILE_NOT_FOUND(error_description='research was not found')
    return path


async def check_access_to_research(con: asyncpg.Connection, user_id: int, research_id: str):
    have_access = await crud.have_access_to_research(con, user_id, research_id)
    if not have_access:
        raise exc.ACCESS_DENIED(error_description='you have not acces to this markup (only creator and markers)')


async def upload_markup(research_id: str, file: UploadFile):
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    loaded = await storage.load_markup(research_id, file)
    if not loaded:
        raise exc.WRONG_FILES_FORMAT(error_description='.json expected')
    

async def get_markers(con: asyncpg.Connection) -> tp.List[sch.Marker]:
    return await crud.get_markers(con)


async def get_tags(con: asyncpg.Connection) -> tp.List[str]:
    return await crud.get_tags(con)
    

async def add_tags(con: asyncpg.Connection, tags: tp.List[str]) -> None:
    await crud.add_tags(con, tags)


async def change_task_status(con: asyncpg.Connection, task_id: str, status: sch.TaskStatus) -> None:
    await crud.change_task_status(con, task_id, status)


async def search_researches(con: asyncpg.Connection, body: tp.Optional[sch.SearchResearchesRequest]) -> sch.SearchResearchesResponse:
    query, tags = (None, None) if body is None else (body.query, body.tags)
    search_result = await crud.search_researches(con, query, tags)

    response = sch.SearchResearchesResponse()
    for row in search_result:
        research = sch.Research.parse_obj(row)
        response.researches.append(research)
    return response


async def search_tasks(con: asyncpg.Connection, body: sch.SearchTasksRequest) -> sch.SearchTaskResponse:
    research_name, status, deadline, created_at, user_id = (None, None, None, None, None) \
                                                            if body is None else \
                                                            (body.research_name, body.status, body.deadline, body.created_at, body.user_id)
    search_result = await crud.search_tasks(con, research_name, status, user_id)
    response = sch.SearchTaskResponse()
    for row in search_result:
        task = sch.Task.parse_obj(row)
        response.tasks.append(task)
    return response
    
                                                   
                                                   