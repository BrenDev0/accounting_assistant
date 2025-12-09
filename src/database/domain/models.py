from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Base(DeclarativeBase):
    pass


class TenantTable(Base):
    __tablename__ = "tenant_tables"

    tenant_table_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False)
    table_name = Column(String, nullable=False)
    create_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())