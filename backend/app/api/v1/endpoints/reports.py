"""
Reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.report import ReportResponse, ReportType
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/enrollment", response_model=ReportResponse)
async def get_enrollment_report(
    course_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Generate enrollment report"""
    report_service = ReportService(db)
    return report_service.generate_enrollment_report(
        course_id=course_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/completion", response_model=ReportResponse)
async def get_completion_report(
    course_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Generate completion rate report"""
    report_service = ReportService(db)
    return report_service.generate_completion_report(
        course_id=course_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/member-progress", response_model=ReportResponse)
async def get_member_progress_report(
    member_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Generate member progress report"""
    report_service = ReportService(db)
    return report_service.generate_member_progress_report(
        member_id=member_id,
        course_id=course_id
    )


@router.get("/export/{report_type}")
async def export_report(
    report_type: ReportType,
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    course_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Export report in specified format"""
    report_service = ReportService(db)
    
    if report_type == ReportType.ENROLLMENT:
        report_data = report_service.generate_enrollment_report(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
    elif report_type == ReportType.COMPLETION:
        report_data = report_service.generate_completion_report(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
    elif report_type == ReportType.MEMBER_PROGRESS:
        report_data = report_service.generate_member_progress_report(
            course_id=course_id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report type"
        )
    
    return report_service.export_report(report_data, format)
