from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.privacy_service import PrivacyService
from app.schemas.privacy import (
    StudentConsentResponse,
    StudentConsentUpdate,
    ConsentWithdrawRequest,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
    AuditLogResponse,
    FairnessEvaluationResponse,
    DataDeletionRequest,
    DataDeletionResponse,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/privacy", tags=["Privacy & Fairness"])


# =========================================================================
# A. STUDENT CONSENT MANAGEMENT
# =========================================================================

@router.get("/consent", response_model=List[StudentConsentResponse], status_code=status.HTTP_200_OK)
def get_all_student_consents(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Granted, Revoked, Pending)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List student consent records with multi-dimensional filtering.
    Requires JWT authentication.
    """
    return PrivacyService.get_all_consents(
        db=db,
        status_filter=status_filter,
        department=department,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/consent/{student_id}", response_model=StudentConsentResponse, status_code=status.HTTP_200_OK)
def get_student_consent(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get consent status and granular permissions for a specific student.
    Requires JWT authentication.
    """
    return PrivacyService.get_student_consent(db=db, student_id=student_id)


@router.put("/consent/{student_id}", response_model=StudentConsentResponse, status_code=status.HTTP_200_OK)
def update_student_consent(
    student_id: str,
    data: StudentConsentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update granular student consent permissions (camera processing, face recognition,
    attendance processing, and emotion inference). Automatically generates audit trail.
    Requires JWT authentication.
    """
    client_ip = request.client.host if request.client else None
    return PrivacyService.update_student_consent(
        db=db,
        student_id=student_id,
        data=data,
        current_user=current_user,
        ip_address=client_ip,
    )


@router.post("/consent/{student_id}/withdraw", response_model=StudentConsentResponse, status_code=status.HTTP_200_OK)
def withdraw_student_consent(
    student_id: str,
    request: Request,
    body: Optional[ConsentWithdrawRequest] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Consent Withdrawal Mechanism: Immediately revokes camera, face recognition, attendance,
    and emotion inference permissions. Blocks automatic camera attendance and emotion inference.
    Requires JWT authentication.
    """
    client_ip = request.client.host if request.client else None
    reason = body.reason if body else "User requested withdrawal"
    return PrivacyService.withdraw_student_consent(
        db=db,
        student_id=student_id,
        reason=reason,
        current_user=current_user,
        ip_address=client_ip,
    )


# =========================================================================
# B. DATA RETENTION & DELETION PROCEDURES
# =========================================================================

@router.get("/retention", response_model=List[RetentionPolicyResponse], status_code=status.HTTP_200_OK)
def get_retention_policies(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get system data retention policies (face embeddings, attendance, raw frames, emotion records).
    Requires JWT authentication.
    """
    return PrivacyService.get_retention_policies(db=db)


@router.put("/retention/{policy_id}", response_model=RetentionPolicyResponse, status_code=status.HTTP_200_OK)
def update_retention_policy(
    policy_id: int,
    data: RetentionPolicyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update retention policy configuration (retention days, description, auto purge).
    Requires JWT authentication.
    """
    client_ip = request.client.host if request.client else None
    return PrivacyService.update_retention_policy(
        db=db,
        policy_id=policy_id,
        data=data,
        current_user=current_user,
        ip_address=client_ip,
    )


@router.post("/retention/purge/{policy_name}", status_code=status.HTTP_200_OK)
def purge_retention_data(
    policy_name: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Execute data retention cleanup procedure for expired records under a specific policy.
    Requires JWT authentication.
    """
    client_ip = request.client.host if request.client else None
    return PrivacyService.purge_retention_data(
        db=db,
        policy_name=policy_name,
        current_user=current_user,
        ip_address=client_ip,
    )


@router.post("/student/{student_id}/purge", response_model=DataDeletionResponse, status_code=status.HTTP_200_OK)
def execute_student_data_purge(
    student_id: str,
    request: Request,
    options: Optional[DataDeletionRequest] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    'Right to be Forgotten' Data Deletion Procedure:
    Permanently purges biometric face embeddings, emotion records, attendance records,
    and revokes consent with an audit trail.
    Requires JWT authentication.
    """
    client_ip = request.client.host if request.client else None
    opt = options or DataDeletionRequest()
    return PrivacyService.execute_student_data_deletion(
        db=db,
        student_id=student_id,
        options=opt,
        current_user=current_user,
        ip_address=client_ip,
    )


# =========================================================================
# C. PRIVACY, SECURITY & AUDIT LOGS
# =========================================================================

@router.get("/audit-logs", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieve immutable audit logs for sensitive operations: consent modification,
    embedding enrollment/deletion, monitoring session start/stop, and retention purges.
    Requires JWT authentication.
    """
    return PrivacyService.get_audit_logs(
        db=db,
        action_filter=action,
        target_type=target_type,
        limit=limit,
        offset=offset,
    )


# =========================================================================
# D. FAIRNESS EVALUATION & LIGHTING BENCHMARKS
# =========================================================================

@router.get("/fairness", response_model=FairnessEvaluationResponse, status_code=status.HTTP_200_OK)
def get_fairness_evaluation(
    current_user=Depends(get_current_user),
):
    """
    Get fairness evaluation, lighting condition comparisons (Standard vs Low-Light vs Glare),
    FAR/FRR biometric metrics, and documented bias limitations.
    Uncollected demographic experiments are strictly labeled 'Evaluation Pending'.
    Requires JWT authentication.
    """
    return PrivacyService.get_fairness_evaluation()
