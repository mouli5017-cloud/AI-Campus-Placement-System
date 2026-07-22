from .student_dashboard import (
    render_placement_prediction,
    render_resume_analysis,
    render_job_matching,
    render_skill_gap_analysis,
    render_interview_prep,
    render_export_reports,
    render_prediction_history,
)

from .admin_dashboard import (
    render_system_overview,
    render_analytics_dashboard,
    render_user_management,
    render_data_management,
)

from .placement_officer_dashboard import (
    render_bulk_resume_screening,
    render_placement_drives,
    render_placement_statistics,
    render_student_lookup,
)

__all__ = [
    "render_placement_prediction",
    "render_resume_analysis",
    "render_job_matching",
    "render_skill_gap_analysis",
    "render_interview_prep",
    "render_export_reports",
    "render_prediction_history",
    "render_system_overview",
    "render_analytics_dashboard",
    "render_user_management",
    "render_data_management",
    "render_bulk_resume_screening",
    "render_placement_drives",
    "render_placement_statistics",
    "render_student_lookup",
]
