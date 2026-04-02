"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    """Response after successful CSV upload"""
    dataset_id: str
    filename: str
    rows: int
    columns: List[str]
    dtypes: Dict[str, str]
    message: str = "Dataset uploaded successfully"


class AskRequest(BaseModel):
    """Request to analyze dataset with natural language question"""
    dataset_id: str = Field(..., description="ID of uploaded dataset")
    question: str = Field(..., min_length=5, description="Natural language question about the data")
    context: Optional[str] = Field(None, description="Additional context or constraints")
    enable_visualization: bool = Field(True, description="Whether to generate visualizations")


class AskResponse(BaseModel):
    """Response after submitting analysis question"""
    task_id: str
    dataset_id: str
    question: str
    generated_code: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = "Task created successfully"


class TaskStatusResponse(BaseModel):
    """Task execution status and results"""
    task_id: str
    dataset_id: str
    question: str
    status: TaskStatus
    generated_code: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    result_files: List[str] = []
    error_message: Optional[str] = None


class ReportResponse(BaseModel):
    """HTML report response"""
    task_id: str
    report_available: bool
    report_path: Optional[str] = None
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime
    version: str = "0.1.0"
