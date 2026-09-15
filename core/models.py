from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DisciplineEnum(str, Enum):
    CIVIL = "Civil"
    PIPING = "Piping"
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    INSTRUMENTATION = "Instrumentation"
    HSE = "HSE"
    COMMISSIONING = "Commissioning"
    GENERAL = "General"

class WBSLevel(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"

class ActivityStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    ON_HOLD = "ON_HOLD"

class DelayCategory(str, Enum):
    MATERIAL = "Material"
    APPROVAL = "Approval"
    OPERATIONAL = "Operational"
    WEATHER = "Weather"
    MANPOWER = "Manpower"
    NONE = "None"

class RoutingStatus(str, Enum):
    AUTO_SOFT_UPDATE = "AUTO_SOFT_UPDATE"
    PLANNER_REVIEW = "PLANNER_REVIEW"
    SUPERVISOR_CLARIFICATION = "SUPERVISOR_CLARIFICATION"
    REJECTED = "REJECTED"

class BaselineActivity(BaseModel):
    activity_id: str
    wbs_level: str
    wbs_code: str
    activity_name: str
    discipline: str
    planned_start: str
    planned_finish: str
    planned_duration_days: int
    predecessors: List[str] = []
    weightage: float = 1.0
    unit_area: str = "General"
    early_start: Optional[int] = None
    early_finish: Optional[int] = None
    late_start: Optional[int] = None
    late_finish: Optional[int] = None
    total_float: Optional[int] = None
    is_critical: bool = False

class ActualActivityState(BaseModel):
    activity_id: str
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    actual_duration_days: Optional[int] = None
    progress_pct: float = 0.0
    evidence_progress_pct: float = 0.0
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    last_updated: str = ""
    evidence_sources: List[str] = []
    delay_reasons: List[str] = []
    blocker_category: Optional[str] = None

class RawExecutionEvent(BaseModel):
    event_id: str
    source_type: str  # "DPR", "EXCEL", "VOICE_AGENT", "SITE_DIARY"
    source_reference: str
    event_date: str
    raw_text: str
    discipline: str
    extracted_activity: str
    reported_status: str
    progress_pct: Optional[float] = None
    quantity_info: Optional[str] = None
    blocker: Optional[str] = None
    delay_category: Optional[str] = None
    supervisor: Optional[str] = None
    text_citation: str = ""

class CandidateMatch(BaseModel):
    activity_id: str
    activity_name: str
    discipline: str
    wbs_code: str
    fuzzy_score: float
    bm25_score: float
    semantic_score: float
    domain_boost: float
    composite_confidence: float  # 0 to 100
    match_rationale: str

class ScheduleUpdateCandidate(BaseModel):
    candidate_id: str
    raw_event: RawExecutionEvent
    top_matches: List[CandidateMatch]
    selected_activity_id: Optional[str] = None
    composite_confidence: float = 0.0
    routing_decision: RoutingStatus = RoutingStatus.PLANNER_REVIEW
    routing_reasons: List[str] = []
    has_contradiction: bool = False
    precedence_violation: bool = False
    contradiction_details: Optional[str] = None
    precedence_details: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    status: str = "PENDING"  # PENDING, COMMITTED, REJECTED
    created_at: str = ""

class AuditLogEntry(BaseModel):
    audit_id: str
    timestamp: str
    activity_id: str
    action: str
    actor: str
    confidence: float
    evidence_hash: str
    raw_text_citation: str
    diff_summary: str
    status_change: str

class EVMMetrics(BaseModel):
    planned_value: float
    earned_value: float
    claimed_value: float
    schedule_variance: float
    schedule_performance_index: float
    critical_path_delay_days: int
    projected_finish_date: str
    as_of_date: str

class InstitutionalMemoryRecord(BaseModel):
    record_id: Optional[int] = None
    activity_id: str
    activity_name: str
    discipline: str
    planned_duration: int
    actual_duration: int
    variance_days: int
    variance_pct: float
    delay_category: str
    delay_cause: str
    productivity_factor: float
    weather_condition: str
    season: str
    notes: str
