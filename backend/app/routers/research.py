from fastapi import APIRouter, Depends, status
from app.services.research_service import ResearchService
from app.schemas.research import ResearchMethodologyResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/research", tags=["Research Methodology"])


@router.get("/methodology", response_model=ResearchMethodologyResponse, status_code=status.HTTP_200_OK)
def get_research_methodology(current_user=Depends(get_current_user)):
    """
    Retrieve comprehensive Research Methodology specifications addressing Review Comment 1:
    - Dataset Overview, Collection Method, and Characteristics
    - Data Preprocessing and Alignment
    - Engagement & Emotion Labeling Procedures
    - Student-Independent Train/Validation/Test Splits & Identity Leakage Prevention
    - Baseline Model Comparison (Haar, MTCNN, SFace, ArcFace)
    - Evaluation Metrics, Confusion Matrix, and 91.4% Accuracy Provenance
    - Reproducibility and Experimental Configuration
    Requires JWT authentication.
    """
    return ResearchService.get_methodology()


@router.get("/benchmarks", status_code=status.HTTP_200_OK)
def get_research_benchmarks(current_user=Depends(get_current_user)):
    """
    Get summarized benchmark comparison and performance metrics.
    Requires JWT authentication.
    """
    meth = ResearchService.get_methodology()
    return {
        "headline_accuracy": meth.performance_summary.get("headline_accuracy"),
        "provenance": meth.performance_summary.get("headline_metric_provenance"),
        "baselines": meth.baseline_comparisons,
        "metrics": meth.evaluation_metrics,
        "confusion_matrix": meth.confusion_matrix,
        "splits_protocol": meth.student_independent_splits,
    }
