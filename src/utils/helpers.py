import os
import sys
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps

import bcrypt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_session_token() -> str:
    return secrets.token_hex(32)


def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_cgpa(cgpa: float) -> bool:
    return 0.0 <= cgpa <= 10.0


def format_currency(amount_lpa: float) -> str:
    if amount_lpa >= 1.0:
        return f"{amount_lpa:.2f} LPA"
    return f"{amount_lpa * 100000:.0f} INR"


def calculate_percentage(part: float, total: float) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default


def format_date(dt: datetime, fmt: str = "%d %B %Y") -> str:
    return dt.strftime(fmt)


def get_time_ago(dt: datetime) -> str:
    now = datetime.now()
    diff = now - dt
    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def clean_text(text: str) -> str:
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,@#$%&*()\-+=/]', '', text)
    return text.strip()


def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def is_valid_pdf(filename: str) -> bool:
    return get_file_extension(filename) == '.pdf'


def format_number(num: float) -> str:
    if num >= 1e7:
        return f"{num / 1e7:.1f} Cr"
    elif num >= 1e5:
        return f"{num / 1e5:.1f} L"
    elif num >= 1e3:
        return f"{num / 1e3:.1f}K"
    return str(round(num, 1))


SKILL_COLORS = {
    "technical": "#1E88E5",
    "soft": "#43A047",
    "domain": "#FB8C00",
}


def get_skill_color(category: str) -> str:
    return SKILL_COLORS.get(category, "#757575")
