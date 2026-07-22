import re
import pdfplumber
import io
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

SECTION_HEADERS = {
    "summary": ["summary", "objective", "profile", "about me", "career objective"],
    "education": ["education", "academic", "qualification", "degree", "university"],
    "experience": ["experience", "work experience", "employment", "internship", "work history"],
    "skills": ["skills", "technical skills", "competencies", "technologies", "proficiencies"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses", "courses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
    "extracurricular": ["extracurricular", "activities", "clubs", "volunteer"],
}


@dataclass
class ParsedResume:
    raw_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = field(default_factory=list)
    education: List[Dict[str, str]] = field(default_factory=list)
    experience_years: float = 0.0
    projects: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    summary: str = ""
    github_url: str = ""
    linkedin_url: str = ""
    total_words: int = 0
    sections_detected: List[str] = field(default_factory=list)


class ResumeParser:
    def __init__(self):
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        self.phone_pattern = re.compile(
            r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
        )
        self.url_pattern = re.compile(
            r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        )
        self.github_pattern = re.compile(
            r'github\.com/[a-zA-Z0-9_-]+'
        )
        self.linkedin_pattern = re.compile(
            r'linkedin\.com/in/[a-zA-Z0-9_-]+'
        )

    def parse_pdf(self, file_content: bytes) -> ParsedResume:
        try:
            text = self._extract_text_from_pdf(file_content)
            return self.parse_text(text)
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise

    def parse_text(self, text: str) -> ParsedResume:
        resume = ParsedResume()
        resume.raw_text = text
        resume.total_words = len(text.split())

        resume.email = self._extract_email(text)
        resume.phone = self._extract_phone(text)
        resume.github_url = self._extract_github(text)
        resume.linkedin_url = self._extract_linkedin(text)
        resume.name = self._extract_name(text)

        resume.sections = self._detect_sections(text)
        resume.sections_detected = list(resume.sections.keys())

        resume.summary = resume.sections.get("summary", "")
        resume.education = self._parse_education(
            resume.sections.get("education", "")
        )
        resume.projects = self._parse_bullet_points(
            resume.sections.get("projects", "")
        )
        resume.certifications = self._parse_bullet_points(
            resume.sections.get("certifications", "")
        )
        resume.experience_years = self._extract_experience_years(
            resume.sections.get("experience", "")
        )

        return resume

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def _extract_email(self, text: str) -> str:
        match = self.email_pattern.search(text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        match = self.phone_pattern.search(text)
        return match.group(0).strip() if match else ""

    def _extract_github(self, text: str) -> str:
        match = self.github_pattern.search(text)
        return f"https://{match.group(0)}" if match else ""

    def _extract_linkedin(self, text: str) -> str:
        match = self.linkedin_pattern.search(text)
        return f"https://{match.group(0)}" if match else ""

    def _extract_name(self, text: str) -> str:
        lines = text.strip().split("\n")
        for line in lines[:5]:
            line = line.strip()
            if (
                2 <= len(line.split()) <= 4
                and not self.email_pattern.search(line)
                and not self.phone_pattern.search(line)
                and not any(c.isdigit() for c in line)
                and len(line) < 50
                and not line.startswith(("http", "www", "linkedin", "github"))
            ):
                return line
        return ""

    def _detect_sections(self, text: str) -> Dict[str, str]:
        lines = text.split("\n")
        sections = {}
        current_section = None
        current_content = []

        for line in lines:
            line_lower = line.strip().lower()
            matched_section = None

            for section_name, headers in SECTION_HEADERS.items():
                for header in headers:
                    if (
                        header in line_lower
                        and len(line.strip()) < 50
                        and line.strip().endswith(()) == False
                    ):
                        if any(kw in line_lower for kw in [
                            ":", "section", "—", "-"
                        ]) or line.strip().upper() == line.strip():
                            matched_section = section_name
                            break
                if matched_section:
                    break

            if matched_section:
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = matched_section
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _parse_education(self, text: str) -> List[Dict[str, str]]:
        education = []
        degree_patterns = [
            r'(B\.?E\.?|B\.?Tech\.?|Bachelor|B\.?S\.?)\s*(?:in\s+)?(\w[\w\s]*?)(?:\s*[,|\n])',
            r'(M\.?Tech\.?|Master|M\.?S\.?)\s*(?:in\s+)?(\w[\w\s]*?)(?:\s*[,|\n])',
            r'(Ph\.?D\.?|Doctorate)\s*(?:in\s+)?(\w[\w\s]*?)(?:\s*[,|\n])',
            r'(Diploma)\s*(?:in\s+)?(\w[\w\s]*?)(?:\s*[,|\n])',
        ]
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match.group(1).strip(),
                    "field": match.group(2).strip() if match.group(2) else "",
                })

        if not education and text.strip():
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines[:3]:
                education.append({"degree": line, "field": ""})

        return education

    def _parse_bullet_points(self, text: str) -> List[str]:
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "• ", "* ", "► ", "→ ", ">> ")):
                items.append(line.lstrip("-•*►→> ").strip())
            elif len(line) > 10 and not line.startswith(("http", "www")):
                items.append(line)
        return items

    def _extract_experience_years(self, text: str) -> float:
        patterns = [
            r'(\d+\.?\d*)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)',
            r'(\d+\.?\d*)\+?\s*years?\s*(?:in|working)',
            r'experience\s*:\s*(\d+\.?\d*)\s*years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        date_range_pattern = r'(\d{4})\s*[-–]\s*(?:present|(\d{4})|current)'
        dates = re.findall(date_range_pattern, text, re.IGNORECASE)
        if dates:
            years = set()
            for date_match in dates:
                years.add(int(date_match[0]))
                if date_match[1]:
                    years.add(int(date_match[1]))
            if len(years) >= 2:
                return max(years) - min(years)

        return 0.0
