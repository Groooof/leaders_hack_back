import pydantic as pd
import datetime as dt
import re
import typing as tp
from enum import Enum


    
class ResearchStatus(str, Enum):
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
    
    
class SearchFilters(pd.BaseModel):
    tags: tp.Optional[tp.List[str]] = None
    marker: tp.Optional[int] = None
    

class Research(pd.BaseModel):
    id: str
    name: str
    description: str
    tags: tp.List[str]
    status: ResearchStatus
    marker: tp.Optional[Marker]

    
class FilterData(pd.BaseModel):
    name: str
    get_values: str    
    
    
# Responses ------------------------------------------------------------------------

class CreateResearchResponse(pd.BaseModel):
    research_id: str
    captures_count: int
    

class GetFiltersResponse(pd.BaseModel):
    filters: tp.List[FilterData]
    
    
class SearchResponse(pd.BaseModel):
    researches: tp.List[Research] = pd.Field(default_factory=list)
    
    
# Requests -------------------------------------------------------------------------    


class ChangeResearchStatusRequest(pd.BaseModel):
    status: ResearchStatus
    
    
class SearchRequest(pd.BaseModel):
    query: tp.Optional[str]
    filters: tp.Optional[SearchFilters] = None
    

class AddTagsRequest(pd.BaseModel):
    tags: tp.List[str]
