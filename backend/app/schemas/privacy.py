from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class StudentConsentBase(BaseModel):
    camera_processing: bool = False
    face_recognition: bool = False
    attendance_processing: bool = False
    emotion_inference: bool = False
    notes: Optional[str] = None


class StudentConsentCreate(StudentConsentBase):
    student_id: str
    status: Optional[str] = "Pending"


class StudentConsentUpdate(BaseModel):
    camera_processing: Optional[bool] = None
    face_recognition: Optional[bool] = None
    attendance_processing: Optional[bool] = None
    emotion_inference: Optional[bool] = None
    status: Optional[str] = None  # "Granted", "Revoked", "Pending", "Partially Granted"
    notes: Optional[str] = None


class ConsentWithdrawRequest(BaseModel):
    reason: Optional[str] = "Student / Guardian requested consent withdrawal"


class StudentConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    student_name: Optional[str] = None
    student_department: Optional[str] = None
    camera_processing: bool
    face_recognition: bool
    attendance_processing: bool
    emotion_inference: bool
    status: str
    consent_timestamp: Optional[datetime] = None
    withdrawn_timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class RetentionPolicyBase(BaseModel):
    policy_name: str
    description: Optional[str] = None
    retention_days: int = 365
    storage_type: str = "Database"
    auto_purge_enabled: bool = True


class RetentionPolicyUpdate(BaseModel):
    retention_days: Optional[int] = None
    description: Optional[str] = None
    auto_purge_enabled: Optional[bool] = None


class RetentionPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_name: str
    description: Optional[str] = None
    retention_days: int
    storage_type: str
    auto_purge_enabled: bool
    last_purged_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime


class LightingBenchmarkItem(BaseModel):
    condition: str
    lux_range: str
    description: str
    samples_tested: Optional[int] = None
    detection_rate: Optional[float] = None
    recognition_accuracy: Optional[float] = None
    far: Optional[float] = None  # False Acceptance Rate
    frr: Optional[float] = None  # False Rejection Rate
    status: str  # "Verified Benchmark" or "Evaluation Pending"


class DemographicBenchmarkItem(BaseModel):
    cohort: str
    description: str
    status: str  # "Evaluation Pending - Formal Audit Underway"
    notes: str
    far: Optional[str] = "Pending"
    frr: Optional[str] = "Pending"
    sample_size: Optional[str] = "Pending Lawful Dataset Authorization"


class FairnessEvaluationResponse(BaseModel):
    system_overview: str
    lawful_collection_statement: str
    privacy_preservation_policy: str
    lighting_benchmarks: List[LightingBenchmarkItem]
    demographic_benchmarks: List[DemographicBenchmarkItem]
    far_overall: Optional[float] = None
    frr_overall: Optional[float] = None
    bias_documentation: List[str]
    systemic_limitations: List[str]
    mitigation_strategies: List[str]


class DataDeletionRequest(BaseModel):
    delete_attendance: bool = False
    delete_emotions: bool = True
    delete_embeddings: bool = True
    confirm: bool = True


class DataDeletionResponse(BaseModel):
    student_id: str
    success: bool
    message: str
    deleted_items: Dict[str, Any]
    timestamp: datetime
