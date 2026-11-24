from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class BaselineModelItem(BaseModel):
    model_name: str
    model_type: str  # Face Detection / Recognition / Emotion
    architecture: str
    input_resolution: str
    accuracy_claimed: Optional[float] = None
    latency_ms: Optional[float] = None
    parameters: Optional[str] = None
    status: str  # "Verified Benchmark", "Published Baseline", or "Pending Evaluation"
    source: str


class ConfusionMatrixData(BaseModel):
    labels: List[str]
    matrix: List[List[float]]
    status: str  # "Verified Benchmark" or "Pending Research Data"
    notes: str


class EvaluationMetricsItem(BaseModel):
    task: str
    model: str
    dataset_split_type: str  # "Student-Independent Split" vs "Random Frame Split"
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    sample_count: Optional[int] = None
    verification_status: str  # "Verified Result" or "Pending Research Data"
    notes: str


class ResearchMethodologyResponse(BaseModel):
    page_title: str
    version: str
    last_updated: str
    
    # 1. Dataset Overview
    dataset_overview: Dict[str, Any]

    # 2. Dataset Collection Method
    collection_method: Dict[str, Any]

    # 3. Dataset Characteristics
    dataset_characteristics: Dict[str, Any]

    # 4. Data Preprocessing
    data_preprocessing: Dict[str, Any]

    # 5. Engagement Labeling Procedure
    engagement_labeling: Dict[str, Any]

    # 6. Emotion Labeling Procedure
    emotion_labeling: Dict[str, Any]

    # 7. Student-Independent Train/Validation/Test Splits
    student_independent_splits: Dict[str, Any]

    # 8. Baseline Model Comparison
    baseline_comparisons: List[BaselineModelItem]

    # 9. Model Evaluation Metrics
    evaluation_metrics: List[EvaluationMetricsItem]

    # 10. Confusion Matrix
    confusion_matrix: ConfusionMatrixData

    # 11. Accuracy, Precision, Recall and F1 Score Summary
    performance_summary: Dict[str, Any]

    # 12. Reproducibility and Experimental Configuration
    reproducibility_config: Dict[str, Any]
