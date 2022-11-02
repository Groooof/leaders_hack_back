import pydantic as pd
import datetime as dt
import re
import typing as tp
from enum import Enum


class CreateResearchResponse(pd.BaseModel):
    research_id: str
    captures_count: int
    