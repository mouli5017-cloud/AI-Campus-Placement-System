import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    recipient: str
    subject: str
    body: str
    email_type: str = "general"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "sent"


class EmailNotificationService:
    def __init__(self):
        self.sent_emails: List[EmailMessage] = []
        self.email_templates = self._load_templates()

    def _load_templates(self) -> Dict:
        return {
            "placement_prediction": {
                "subject": "Your Placement Prediction Result - Campus AI",
                "body": (
                    "Dear {name},\n\n"
                    "Your placement prediction has been generated.\n\n"
                    "Placement Probability: {probability}%\n"
                    "Prediction: {status}\n"
                    "Risk Level: {risk_level}\n\n"
                    "Key Suggestions:\n{suggestions}\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
            "resume_analyzed": {
                "subject": "Resume Analysis Complete - ATS Score: {ats_score}",
                "body": (
                    "Dear {name},\n\n"
                    "Your resume has been analyzed successfully.\n\n"
                    "ATS Score: {ats_score}/100\n"
                    "Grade: {grade}\n"
                    "Skills Found: {skills_count}\n\n"
                    "Improvements:\n{improvements}\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
            "job_match": {
                "subject": "New Job Matches Found - Campus AI",
                "body": (
                    "Dear {name},\n\n"
                    "We found {match_count} new job matches for your profile.\n\n"
                    "Top Matches:\n{top_matches}\n\n"
                    "Login to view details and apply.\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
            "skill_gap_alert": {
                "subject": "Skill Gap Alert - Action Required",
                "body": (
                    "Dear {name},\n\n"
                    "Our analysis identified skill gaps for your target role: {target_role}\n\n"
                    "Missing Skills:\n{missing_skills}\n\n"
                    "Recommended Courses:\n{recommendations}\n\n"
                    "Start learning today to improve your placement chances!\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
            "placement_update": {
                "subject": "Placement Drive Update - {company_name}",
                "body": (
                    "Dear {name},\n\n"
                    "A new placement drive has been announced.\n\n"
                    "Company: {company_name}\n"
                    "Role: {job_title}\n"
                    "Min CGPA: {min_cgpa}\n"
                    "Salary Range: {min_salary} - {max_salary} LPA\n"
                    "Location: {location}\n\n"
                    "Apply before the deadline!\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
            "weekly_report": {
                "subject": "Weekly Placement Report - Campus AI",
                "body": (
                    "Dear {name},\n\n"
                    "Here is your weekly placement preparation report:\n\n"
                    "Predictions Made: {predictions_count}\n"
                    "Current Placement Probability: {current_probability}%\n"
                    "Skills Learned This Week: {skills_learned}\n"
                    "Companies to Target: {target_companies}\n\n"
                    "Keep up the good work!\n\n"
                    "Best regards,\nCampus Placement AI Team"
                ),
            },
        }

    def send_notification(
        self, template_key: str, recipient: str, **kwargs
    ) -> EmailMessage:
        template = self.email_templates.get(template_key)
        if not template:
            logger.warning(f"Template '{template_key}' not found")
            return None

        try:
            subject = template["subject"].format(**kwargs)
            body = template["body"].format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            subject = template["subject"]
            body = template["body"]

        email = EmailMessage(
            recipient=recipient,
            subject=subject,
            body=body,
            email_type=template_key,
        )
        self.sent_emails.append(email)
        logger.info(f"Email sent to {recipient}: {subject}")
        return email

    def send_placement_prediction(
        self, name: str, email: str, result: Dict
    ) -> EmailMessage:
        suggestions = "\n".join(
            f"- {s}" for s in result.get("suggestions", [])
        )
        return self.send_notification(
            "placement_prediction",
            recipient=email,
            name=name,
            probability=result.get("probability_placed", 0),
            status="PLACED" if result.get("placed") else "NOT PLACED",
            risk_level=result.get("risk_level", "Unknown"),
            suggestions=suggestions or "No suggestions available.",
        )

    def send_resume_analysis(
        self, name: str, email: str, ats_result: Dict
    ) -> EmailMessage:
        improvements = "\n".join(
            f"- {i}" for i in ats_result.get("improvements", [])
        )
        return self.send_notification(
            "resume_analyzed",
            recipient=email,
            name=name,
            ats_score=ats_result.get("overall_score", 0),
            grade=ats_result.get("grade", "N/A"),
            skills_count=len(ats_result.get("section_scores", {})),
            improvements=improvements or "No improvements needed.",
        )

    def send_job_matches(
        self, name: str, email: str, matches: List[Dict]
    ) -> EmailMessage:
        top = matches[:3] if matches else []
        top_str = "\n".join(
            f"- {m.get('company', 'N/A')} ({m.get('overall_match', 0):.0f}% match)"
            for m in top
        )
        return self.send_notification(
            "job_match",
            recipient=email,
            name=name,
            match_count=len(matches),
            top_matches=top_str or "No matches found.",
        )

    def send_skill_gap_alert(
        self, name: str, email: str, role: str,
        missing: List[str], recs: List[Dict]
    ) -> EmailMessage:
        skills_str = "\n".join(f"- {s}" for s in missing)
        recs_str = "\n".join(
            f"- {r.get('course', 'N/A')} ({r.get('platform', 'N/A')})"
            for r in recs[:5]
        )
        return self.send_notification(
            "skill_gap_alert",
            recipient=email,
            name=name,
            target_role=role,
            missing_skills=skills_str,
            recommendations=recs_str,
        )

    def get_sent_emails(self) -> List[Dict]:
        return [
            {
                "recipient": e.recipient,
                "subject": e.subject,
                "type": e.email_type,
                "timestamp": e.timestamp,
                "status": e.status,
            }
            for e in self.sent_emails
        ]

    def get_email_count(self) -> int:
        return len(self.sent_emails)

    def get_emails_by_type(self, email_type: str) -> List[EmailMessage]:
        return [e for e in self.sent_emails if e.email_type == email_type]
