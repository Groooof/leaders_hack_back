import pydantic as pd
import datetime as dt
import uuid
import typing as tp
from enum import Enum


class TaskStatus(str, Enum):
    new = 'Новое'
    in_process = 'В работе'
    completed = 'Завершено'
    on_pause = 'На паузе'
    

class Filters(str, Enum):
    tags = 'tags'
    markers = 'markers'
    
    
class Marker(pd.BaseModel):
    id: int
    name: str
    surname: str
    patronymic: tp.Optional[str]
    

class Research(pd.BaseModel):
    id: tp.Union[str, uuid.UUID]
    name: str
    description: str
    tasks_count: int
    tags: tp.List[str]


class Task(pd.BaseModel):
    task_id: int
    research_id: tp.Union[str, uuid.UUID]
    user_id: int
    user_name: str
    user_surname: str
    user_patronymic: str
    task_deadline: dt.datetime
    task_created_at: dt.datetime
    task_status: TaskStatus
    
    
class FilterData(pd.BaseModel):
    name: str
    get_values: str    
    
    
# Responses ------------------------------------------------------------------------

class CreateResearchResponse(pd.BaseModel):
    research_id: str
    captures_count: int
    

class GetFiltersResponse(pd.BaseModel):
    filters: tp.List[FilterData]
    
    
class SearchResearchesResponse(pd.BaseModel):
    researches: tp.List[Research] = pd.Field(default_factory=list)
    
    
class SearchTaskResponse(pd.BaseModel):
    tasks: tp.List[Task] = pd.Field(default_factory=list)
    
    
class CreateTaskResponse(pd.BaseModel):
    id: int
    created_at: dt.datetime
    status: TaskStatus

    
# Requests -------------------------------------------------------------------------    


class ChangeTaskStatusRequest(pd.BaseModel):
    status: TaskStatus
    
    
class SearchResearchesRequest(pd.BaseModel):
    query: tp.Optional[str] = None
    tags: tp.Optional[tp.List[str]] = None
    
    
class SearchTasksRequest(pd.BaseModel):
    user_id: tp.Optional[int]
    research_name: tp.Optional[str]
    status: tp.Optional[TaskStatus]
    deadline: tp.Optional[dt.datetime]
    created_at: tp.Optional[dt.datetime]
    

class AddTagsRequest(pd.BaseModel):
    tags: tp.List[str]


class CreateTaskRequest(pd.BaseModel):
    research_id: str
    user_id: int
    deadline: dt.datetime
    
