import pydantic as pd
import datetime as dt
import re
import typing as tp
from enum import Enum


class CreateResearchResponse(pd.BaseModel):
    research_id: str
    captures_count: int
    
    
class ResearchStatus(str, Enum):
    new = 'Новое'
    in_process = 'В работе'
    completed = 'Завершено'
    on_pause = 'На паузе'
    

class Filters(str, Enum):
    tags = 'tags'
    markers = 'markers'
    
    
class Tag(pd.BaseModel):
    name: str
    
    
class Marker(pd.BaseModel):
    id: int
    name: str
    surname: str
    patronymic: tp.Optional[str]
    
    
class Filter(pd.BaseModel):
    name: Filters
    values: tp.List[tp.Any]
    
    
class TagFilter(Filter):
    name: Filters = Filters.tags
    values: tp.List[Tag]
    

class MarkerFilter(Filter):
    name: Filters = Filters.markers
    values: tp.List[Marker]
    
    
class GetFiltersResponse(pd.BaseModel):
    filters: tp.List[tp.Union[TagFilter, MarkerFilter]] = pd.Field(default_factory=list)

    
class AddTagsRequest(pd.BaseModel):
    tags: tp.List[str]
    
    
class ChangeResearchStatusRequest(pd.BaseModel):
    status: ResearchStatus
    
    
class SearchFilters(pd.BaseModel):
    tags: tp.Optional[tp.List[str]] = None
    marker: tp.Optional[int] = None
    
    
class SearchRequest(pd.BaseModel):
    query: tp.Optional[str]
    filters: tp.Optional[SearchFilters] = None
    

class Research(pd.BaseModel):
    id: str
    name: str
    description: str
    tags: tp.List[str]
    status: ResearchStatus
    marker: tp.Optional[Marker]
    
    
class SearchResponse(pd.BaseModel):
    researches: tp.List[Research] = pd.Field(default_factory=list)
    
    
    