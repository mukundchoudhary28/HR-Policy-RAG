
from pydantic import BaseModel, model_validator
from typing import Literal, List, Optional, Dict

class Filter(BaseModel):
    doc_type: Optional[Literal['leave', 'holiday', 'payroll', 'benefits', 'conduct', 'work', 'general']] = None
    year: Optional[int] = None
    region: Optional[List[Literal['US', 'IN', 'UK', 'EU', 'APAC', 'Global']]] = None
    is_latest: Optional[str] = None

    @model_validator(mode="after")
    def set_is_latest(self):
        if self.year is not None:
            self.is_latest = None
        else:
            self.is_latest = "Yes"
        return self

class ResponseSchema(BaseModel):
    answer: str
    sources: str 
