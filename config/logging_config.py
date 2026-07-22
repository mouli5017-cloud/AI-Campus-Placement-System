import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_to_file:
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"app_{today}.log")

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        error_file = os.path.join(LOG_DIR, f"errors_{today}.log")
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

    logger = logging.getLogger("campus_ai")
    logger.info(f"Logging initialized at {log_level} level")
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class PerformanceLogger:
    def __init__(self, operation: str):
        self.operation = operation
        self.logger = logging.getLogger("campus_ai.performance")
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        if exc_type:
            self.logger.error(
                f"{self.operation} failed after {elapsed:.3f}s: {exc_val}"
            )
        else:
            self.logger.info(
                f"{self.operation} completed in {elapsed:.3f}s"
            )
        return False


class APILogger:
    def __init__(self):
        self.logger = logging.getLogger("campus_ai.api")

    def log_request(self, method: str, endpoint: str, user: str = "anonymous"):
        self.logger.info(f"REQUEST  | {method} {endpoint} | User: {user}")

    def log_response(self, method: str, endpoint: str, status: int, duration: float):
        self.logger.info(
            f"RESPONSE | {method} {endpoint} | Status: {status} | {duration:.3f}s"
        )

    def log_error(self, endpoint: str, error: str):
        self.logger.error(f"ERROR    | {endpoint} | {error}")


class PredictionLogger:
    def __init__(self):
        self.logger = logging.getLogger("campus_ai.predictions")

    def log_prediction(self, model: str, user: str, result: dict):
        self.logger.info(
            f"PREDICTION | Model: {model} | User: {user} | "
            f"Result: {result.get('placed', 'N/A')} | "
            f"Confidence: {result.get('confidence', 'N/A')}%"
        )

    def log_model_training(self, model: str, metrics: dict):
        self.logger.info(
            f"TRAINING | Model: {model} | "
            f"Metrics: {metrics}"
        )

    def log_model_load(self, model: str, success: bool):
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"MODEL_LOAD | {model} | {status}")


class ResumeLogger:
    def __init__(self):
        self.logger = logging.getLogger("campus_ai.resume")

    def log_upload(self, user: str, filename: str, size: int):
        self.logger.info(
            f"UPLOAD | User: {user} | File: {filename} | Size: {size} bytes"
        )

    def log_parse(self, filename: str, sections: list, skills: int):
        self.logger.info(
            f"PARSE | File: {filename} | "
            f"Sections: {len(sections)} | Skills: {skills}"
        )

    def log_ats_score(self, filename: str, score: float, grade: str):
        self.logger.info(
            f"ATS | File: {filename} | Score: {score} | Grade: {grade}"
        )


class DatabaseLogger:
    def __init__(self):
        self.logger = logging.getLogger("campus_ai.database")

    def log_query(self, query_type: str, table: str, rows: int = 0):
        self.logger.debug(
            f"QUERY | Type: {query_type} | Table: {table} | Rows: {rows}"
        )

    def log_connection(self, status: str):
        self.logger.info(f"DB_CONNECTION | {status}")

    def log_error(self, operation: str, error: str):
        self.logger.error(f"DB_ERROR | {operation} | {error}")
