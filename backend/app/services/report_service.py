"""
Report service layer
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import csv
import io

from app.schemas.report import ReportResponse, ReportData, ReportType
from app.models.course import Course as CourseModel
from app.models.enrollment import CourseEnrollment as EnrollmentModel
from app.models.progress import ContentCompletion as ProgressModel
from app.models.member import People as PeopleModel


class ReportService:
    """Service for report generation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        # Use SQLAlchemy func.count with specific columns to avoid loading models with missing columns
        from sqlalchemy import func
        
        # Get total courses - use direct count query to avoid loading model columns
        total_courses = self.db.query(func.count(CourseModel.id)).scalar() or 0
        
        # Get total enrollments
        total_enrollments = self.db.query(func.count(EnrollmentModel.id)).scalar() or 0
        
        # Get active courses - use direct count with filter
        active_courses = self.db.query(func.count(CourseModel.id)).filter(CourseModel.is_active == True).scalar() or 0
        
        # Get completed enrollments
        completed_enrollments = self.db.query(func.count(EnrollmentModel.id)).filter(EnrollmentModel.status == "completed").scalar() or 0
        
        # Get total members
        total_members = self.db.query(func.count(PeopleModel.id)).filter(PeopleModel.is_active == True).scalar() or 0
        
        # Calculate completion rate
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        return {
            "total_courses": total_courses,
            "active_courses": active_courses,
            "total_enrollments": total_enrollments,
            "completed_enrollments": completed_enrollments,
            "total_members": total_members,
            "completion_rate": round(completion_rate, 2)
        }
    
    def get_completion_trends(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        course_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Get completion trends data"""
        # For now, return mock data since we don't have real completion data yet
        # In a real implementation, this would query actual completion data
        
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
        
        # Generate mock trend data
        trends = []
        current_date = start_date
        while current_date <= end_date:
            trends.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "completions": 0,  # Would be actual completion count
                "enrollments": 0   # Would be actual enrollment count
            })
            # Use timedelta to properly increment date
            current_date = current_date + timedelta(days=1)
        
        return {
            "trends": trends,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            },
            "course_ids": course_ids or []
        }
    
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
            query = query.filter(EnrollmentModel.enrollment_date >= start_date)
        if end_date:
            query = query.filter(EnrollmentModel.enrollment_date <= end_date)
        
        enrollments = query.all()
        
        headers = ["ID", "Course", "Member", "Enrolled Date", "Status", "Notes"]
        rows = []
        
        for enrollment in enrollments:
            rows.append([
                enrollment.id,
                enrollment.course.title if enrollment.course else "N/A",
                f"{enrollment.people.first_name} {enrollment.people.last_name}" if enrollment.people else "N/A",
                enrollment.enrollment_date.strftime("%Y-%m-%d") if enrollment.enrollment_date else "N/A",
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
            course_name = enrollment.course.title if enrollment.course else "Unknown"
            course_counts[course_name] = course_counts.get(course_name, 0) + 1
        return course_counts
