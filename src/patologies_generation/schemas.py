import pydantic as pd
import typing as tp 
from enum import Enum


class Type(str, Enum):
    covid = 'covid'
    cancer = 'cancer'
    metastat = 'metastat'
    
    
class Localization(str, Enum):
    right_up = 'r_u'
    right_middle = 'r_m'
    right_bottom = 'r_b'
    left_up = 'l_u'
    left_middle = 'l_m'
    left_bottom = 'l_b'
    
    
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
    localization: Localization
    count: Count
    size_mm: SizeMm


class GetParamsResponse(pd.BaseModel):
    type: tp.List[Type]
    localization: tp.List[Localization]
    count: tp.List[Count]
    size_mm: tp.List[SizeMm]


class LoadResponse(pd.BaseModel):
    loaded: int
    id: str
    

class GeneratePatologiesRequest(pd.BaseModel):
    params: GenerationParams
