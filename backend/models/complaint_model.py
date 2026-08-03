from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_source = Column(String)
    customer_name = Column(String)
    product_name = Column(String)
    product_strength = Column(String)
    batch_number = Column(String)
    affected_quantity = Column(String)
    manufacturing_date = Column(String)
    expiry_date = Column(String)
    complaint_date = Column(String)
    originating_site = Column(String)
    impacted_materials = Column(String)
    complaint_category = Column(String)
    description = Column(Text)
    structured_summary = Column(Text)
    severity = Column(String)
    priority = Column(String)
    suggested_action = Column(Text)
    initial_risk_assessment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())