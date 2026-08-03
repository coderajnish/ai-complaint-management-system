from pydantic import BaseModel
from typing import Optional

class ComplaintBase(BaseModel):
    complaint_source: Optional[str]
    customer_name: Optional[str]
    product_name: Optional[str]
    product_strength: Optional[str]
    batch_number: Optional[str]
    affected_quantity: Optional[str]
    severity: Optional[str]
    priority: Optional[str]
    description: Optional[str]
    initial_risk_assessment: Optional[str]


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintResponse(ComplaintBase):
    id: int

    class Config:
        from_attributes = True