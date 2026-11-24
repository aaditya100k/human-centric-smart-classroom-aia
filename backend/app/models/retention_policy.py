from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    policy_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    retention_days = Column(Integer, default=365, nullable=False)  # 0 indicates ephemeral RAM-only retention
    storage_type = Column(String(100), default="Database / Vector Store", nullable=False)
    auto_purge_enabled = Column(Boolean, default=True, nullable=False)
    last_purged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
