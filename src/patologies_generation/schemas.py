import pydantic as pd
import typing as tp 
from enum import Enum


class Type(str, Enum):
    covid = 'covid'
    cancer = 'cancer'
    metastat = 'metastat'
    
    
class Lung(str, Enum):
    right = 'right'
    left = 'left'
    
    
class Lobe(str, Enum):
    up = 'up'
    middle = 'middle'
    bottom = 'bottom'
    
    
class Count(str, Enum):
    singular = 'singular'
    few = 'few'
    multiple = 'multiple'
    
    
class SizeMm(str, Enum):
    lt_5 = '_5'
    f_5_t_10 = '5_10'
    f_10_t_20 = '10_20'
    gt_20 = '20_'
    
    
class GenerationParams(pd.BaseModel):
    type: Type
    lung: Lung
    lobe: Lobe
    count: Count
    size_mm: SizeMm


class GetParamsResponse(pd.BaseModel):
    type: tp.List[Type]
    lung: tp.List[Lung]
    lobe: tp.List[Lobe]
    count: tp.List[Count]
    size_mm: tp.List[SizeMm]


class LoadResponse(pd.BaseModel):
    loaded: int
    id: str
    

class GeneratePatologiesRequest(pd.BaseModel):
    params: GenerationParams
