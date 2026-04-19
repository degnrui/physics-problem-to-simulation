from typing import Any, Dict, List, Literal, Optional, TypedDict


class StageStatus(TypedDict, total=False):
    name: str
    status: Literal["pending", "running", "approved", "needs_repair", "failed", "skipped"]
    attempts: int
    score: int
    issues: List[Dict[str, Any]]


class RunStateContract(TypedDict, total=False):
    run_id: str
    request_text: str
    request_mode: Literal["new_simulation", "revision_existing_simulation"]
    request_profile: Dict[str, Any]
    workflow_plan: List[str]
    active_stage: Optional[str]
    artifacts: Dict[str, Dict[str, Any]]
    approved_artifacts: Dict[str, Dict[str, Any]]
    stage_status: Dict[str, StageStatus]
    execution_trace: List[Dict[str, Any]]
    runtime_package: Optional[Dict[str, Any]]
    generated_files: Dict[str, str]
    delivery_runtime: Optional[Dict[str, Any]]
    final_result: Optional[Dict[str, Any]]
