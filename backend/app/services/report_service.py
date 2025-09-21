"""
Report service layer
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import csv
import io

from app.schemas.report import ReportResponse, ReportData, ReportType
from app.models.course import Course as CourseModel
from app.models.enrollment import Enrollment as EnrollmentModel
from app.models.progress import Progress as ProgressModel


class ReportService:
    """Service for report generation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_enrollment_report(
        self,
        course_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReportResponse:
        """Generate enrollment report"""
        query = self.db.query(EnrollmentModel)
        
        if course_id:
            query = query.filter(EnrollmentModel.course_id == course_id)
        if start_date:
            query = query.filter(EnrollmentModel.enrolled_at >= start_date)
        if end_date:
            query = query.filter(EnrollmentModel.enrolled_at <= end_date)
        
        enrollments = query.all()
        
        headers = ["ID", "Course", "Member", "Enrolled Date", "Status", "Notes"]
        rows = []
        
        for enrollment in enrollments:
            rows.append([
                enrollment.id,
                enrollment.course.name if enrollment.course else "N/A",
                f"{enrollment.member.first_name} {enrollment.member.last_name}" if enrollment.member else "N/A",
                enrollment.enrolled_at.strftime("%Y-%m-%d"),
                enrollment.status,
                enrollment.notes or ""
            ])
        
        summary = {
            "total_enrollments": len(enrollments),
            "by_status": self._count_by_status(enrollments),
            "by_course": self._count_by_course(enrollments)
        }
        
        return ReportResponse(
            report_type=ReportType.ENROLLMENT,
            generated_at=datetime.utcnow(),
            filters={
                "course_id": course_id,
                "start_date": start_date,
                "end_date": end_date
            },
            data=ReportData(headers=headers, rows=rows, summary=summary),
            total_records=len(enrollments)
        )
    
    def generate_completion_report(
        self,
        course_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReportResponse:
        """Generate completion rate report"""
        # Implementation for completion report
        headers = ["Course", "Total Enrollments", "Completed", "Completion Rate"]
        rows = []
        summary = {}
        
        return ReportResponse(
            report_type=ReportType.COMPLETION,
            generated_at=datetime.utcnow(),
            filters={
                "course_id": course_id,
                "start_date": start_date,
                "end_date": end_date
            },
            data=ReportData(headers=headers, rows=rows, summary=summary),
            total_records=0
        )
    
    def generate_member_progress_report(
        self,
        member_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> ReportResponse:
        """Generate member progress report"""
        # Implementation for member progress report
        headers = ["Member", "Course", "Module", "Progress %", "Completed Date"]
        rows = []
        summary = {}
        
        return ReportResponse(
            report_type=ReportType.MEMBER_PROGRESS,
            generated_at=datetime.utcnow(),
            filters={
                "member_id": member_id,
                "course_id": course_id
            },
            data=ReportData(headers=headers, rows=rows, summary=summary),
            total_records=0
        )
    
    def export_report(self, report: ReportResponse, format: str) -> Dict[str, Any]:
        """Export report in specified format"""
        if format == "csv":
            return self._export_csv(report)
        elif format == "pdf":
            return self._export_pdf(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_csv(self, report: ReportResponse) -> Dict[str, Any]:
        """Export report as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(report.data.headers)
        
        # Write data rows
        for row in report.data.rows:
            writer.writerow(row)
        
        return {
            "content": output.getvalue(),
            "content_type": "text/csv",
            "filename": f"{report.report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    def _export_pdf(self, report: ReportResponse) -> Dict[str, Any]:
        """Export report as PDF"""
        # Implementation for PDF export
        return {
            "content": "PDF content placeholder",
            "content_type": "application/pdf",
            "filename": f"{report.report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    
    def _count_by_status(self, enrollments: List[EnrollmentModel]) -> Dict[str, int]:
        """Count enrollments by status"""
        status_counts = {}
        for enrollment in enrollments:
            status_counts[enrollment.status] = status_counts.get(enrollment.status, 0) + 1
        return status_counts
    
    def _count_by_course(self, enrollments: List[EnrollmentModel]) -> Dict[str, int]:
        """Count enrollments by course"""
        course_counts = {}
        for enrollment in enrollments:
            course_name = enrollment.course.name if enrollment.course else "Unknown"
            course_counts[course_name] = course_counts.get(course_name, 0) + 1
        return course_counts
