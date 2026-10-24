import json

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from .config import BASE_DIR
from .models import NAME_MAX, COUNTRY_MAX, VILLAGE_MAX, STATE_MAX, DISTRICT_MAX, WORK_MAX


with open(BASE_DIR / "static" / "data" / "india-states-districts.json", encoding="utf-8") as f:
    STATES_DISTRICTS = json.load(f)



class RegistrationIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=NAME_MAX)
    age: int = Field(gt=0, lt=120)
    mobile: str = Field(min_length=1)
    work: str = Field(min_length=1, max_length=WORK_MAX)
    village: str = Field(min_length=1, max_length=VILLAGE_MAX)
    state: str = Field(min_length=1, max_length=STATE_MAX)
    district: str = Field(min_length=1, max_length=DISTRICT_MAX)
    country: str = Field(default="India", max_length=COUNTRY_MAX)
    
    
    @field_validator("mobile")
    @classmethod
    def mobile_must_be_valid(cls, v):
        if not v.isdigit():
            raise ValueError("must contain digits only")
        if len(v) != 10:
            raise ValueError("must be exactly 10 digits")
        return v


    @field_validator("state")
    @classmethod
    def state_must_exist(cls, v):
        if v not in STATES_DISTRICTS:
            raise ValueError("must be a valid state")
        return v

    @field_validator("district")
    @classmethod
    def district_must_belong_to_state(cls, v, info: ValidationInfo):
        state = info.data.get("state")
        if state in STATES_DISTRICTS and v not in STATES_DISTRICTS[state]:
            raise ValueError("does not belong to the selected state")
        return v