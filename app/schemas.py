from pydantic import BaseModel, condecimal, Field
from datetime import datetime
from typing import Optional

class ClaimBase(BaseModel):
    serviceDate: Optional[datetime] = Field(None, alias="service date")
    submittedprocedure: str  = Field(alias="submitted procedure")
    quadrant: Optional[str] = None # All fields except *”quadrant”* are required
    plangroup: Optional[str] = Field(alias="plan/group #")
    subscriber: Optional[str] = Field(alias="subscriber #")
    providernpi: int = Field(alias="provider npi")
    providerfees: condecimal(max_digits=10, decimal_places=2) = Field(alias="provider fees")
    allowedfees: condecimal(max_digits=10, decimal_places=2) = Field(alias="allowed fees")
    membercoinsurance: condecimal(max_digits=10, decimal_places=2) = Field(alias="member coinsurance")
    membercopay: condecimal(max_digits=10, decimal_places=2) = Field(alias="member copay")
    netfee: condecimal(max_digits=10, decimal_places=2) = None


class ClaimCreate(ClaimBase):
    pass

class Claim(ClaimBase):
    id: int

    class Config:
        validate_by_name = True
        populate_by_name = True
        #by_alias = True
