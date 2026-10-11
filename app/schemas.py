from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import NAME_MAX, COUNTRY_MAX, VILLAGE_MAX, STATE_MAX, DISTRICT_MAX, WORK_MAX


class RegistrationIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=NAME_MAX)
    age: int = Field(gt=0, lt=120)
    mobile: str = Field(min_length=1)
    work: str = Field(min_length=1, max_length=WORK_MAX)
    village: str = Field(min_length=1, max_length=VILLAGE_MAX)
    district: str = Field(min_length=1, max_length=DISTRICT_MAX)
    state: str = Field(min_length=1, max_length=STATE_MAX)
    country: str = Field(default="India", max_length=COUNTRY_MAX)
    
    

    @field_validator("mobile")
    @classmethod
    def mobile_must_be_valid(cls, v):
        if not v.isdigit():
            raise ValueError("must contain digits only")
        if len(v) != 10:
            raise ValueError("must be exactly 10 digits")
        return v