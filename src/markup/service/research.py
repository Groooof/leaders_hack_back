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


async def check_access_to_research(con: asyncpg.Connection, user_id: int, research_id: str):
    have_access = await crud.have_access_to_research(con, user_id, research_id)
    if not have_access:
        raise exc.ACCESS_DENIED(error_description='you have not acces to this markup (only creator and markers)')


async def upload_markup(research_id: str, file: UploadFile):
    storage = utils.ResearchesStorage(config.RESEARCHES_PATH)
    loaded = await storage.load_markup(research_id,  file)
    if not loaded:
        raise exc.WRONG_FILES_FORMAT(error_description='.json expected')


async def get_search_filters(con: asyncpg.Connection, user_role: str) -> sch.GetFiltersResponse:
    response = sch.GetFiltersResponse()
    tags = await crud.get_tags(con)
    tags_filter = sch.TagFilter(values=tags)
    response.filters.append(tags_filter)
    
    if user_role == 'moderator':
        markers = await crud.get_markers(con)
        markers_filter = sch.MarkerFilter(values=markers)
        response.filters.append(markers_filter)
        
    return response


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
        # for item in row.items():
            research_id = str(row['research_id'])
            research_name = row['research_name']
            research_description = row['research_description']
            research_status = row['research_status']
            research_tags = row['research_tags']
            marker_id = row['marker_id']
            marker_name = row['marker_name']
            marker_surname = row['marker_surname']
            marker_patronymic = row['marker_patronymic']
            marker = sch.Marker(id=marker_id,
                                name=marker_name,
                                surname=marker_surname,
                                patronymic=marker_patronymic) if marker_id is not None else None
            research = sch.Research(id=research_id,
                                    name=research_name,
                                    description=research_description,
                                    status=research_status,
                                    tags=research_tags,
                                    marker=marker)
            response.researches.append(research)
    return response