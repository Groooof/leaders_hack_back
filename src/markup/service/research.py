import typing as tp
import pathlib

import asyncpg
from fastapi import UploadFile

from src import config
from src.markup import crud
from src.markup import utils
from src.markup import schemas as sch   
from src import exceptions as exc


async def create_research(con: asyncpg.Connection, creator_id: str, name: str, description: str, tags: tp.List[str]) -> str:
    research_id = await crud.create_research(con, creator_id, name, description, tags)
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    storage.create_empty_research(research_id)
    return research_id


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


async def change_research_status(con: asyncpg.Connection, research_id: str, status: sch.ResearchStatus) -> None:
    await crud.change_research_status(con, research_id, status)


async def search(con: asyncpg.Connection, query: tp.Optional[str], filters: sch.SearchFilters) -> sch.SearchResponse:
    tags = filters.tags if filters is not None else None
    marker = filters.marker if filters is not None else None
    search_result = await crud.search(con, query, tags, marker)

    response = sch.SearchResponse()
    for row in search_result:
        marker = sch.Marker(id=row['marker_id'],
                            name=row['marker_name'],
                            surname=row['marker_surname'],
                            patronymic=row['marker_patronymic']) if row['marker_id'] is not None else None
        research = sch.Research(id=str(row['research_id']),
                                name=row['research_name'],
                                description=row['research_description'],
                                status=row['research_status'],
                                tags=row['research_tags'],
                                marker=marker)
        response.researches.append(research)
    return response