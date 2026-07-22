"""
Application Initializer
Sets up the application environment, generates data, and verifies system health.
"""
import os
import sys
import json
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import config
from config.logging_config import setup_logging, get_logger

logger = get_logger("campus_ai.initializer")


def print_banner():
    banner = """
    ============================================================
                                                             
      AI-Powered Campus Placement Prediction                 
      & Intelligent Resume Screening System                  
                                                             
      Version: {version:<45s} 
      Build:   {date:<45s} 
                                                             
    ============================================================
    """.format(version=config.APP_VERSION, date=datetime.now().strftime("%Y-%m-%d"))
    print(banner)


def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        logger.error(f"Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    logger.info(f"Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def check_dependencies():
    required = [
        "streamlit", "pandas", "numpy", "sklearn", "xgboost",
        "pdfplumber", "plotly", "pymysql", "sqlalchemy", "bcrypt"
    ]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.info("Run: pip install -r requirements.txt")
        return False

    logger.info("All required packages installed - OK")
    return True


def check_spacy():
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy en_core_web_sm model loaded - OK")
        return True
    except OSError:
        logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        logger.error(f"spaCy check failed: {e}")
        return False


def generate_datasets():
    logger.info("Generating datasets...")
    try:
        from data.generate_datasets import (
            generate_placement_dataset,
            generate_salary_dataset,
            generate_job_postings
        )

        output_dir = os.path.join("data", "datasets")
        os.makedirs(output_dir, exist_ok=True)

        placement_path = os.path.join(output_dir, "placement_dataset.csv")
        if not os.path.exists(placement_path):
            df = generate_placement_dataset(5000)
            df.to_csv(placement_path, index=False)
            logger.info(f"  Generated placement dataset: {len(df)} samples")
        else:
            logger.info("  Placement dataset already exists - skipping")

        salary_path = os.path.join(output_dir, "salary_dataset.csv")
        if not os.path.exists(salary_path):
            df2 = generate_salary_dataset(5000)
            df2.to_csv(salary_path, index=False)
            logger.info(f"  Generated salary dataset: {len(df2)} samples")
        else:
            logger.info("  Salary dataset already exists - skipping")

        jobs_path = os.path.join(output_dir, "job_postings.csv")
        if not os.path.exists(jobs_path):
            df3 = generate_job_postings()
            df3.to_csv(jobs_path, index=False)
            logger.info(f"  Generated job postings: {len(df3)} records")
        else:
            logger.info("  Job postings already exist - skipping")

        return True
    except Exception as e:
        logger.error(f"Dataset generation failed: {e}")
        return False


def pretrain_models():
    logger.info("Pre-training ML models...")
    try:
        from src.ml.placement_model import PlacementPredictor
        from src.ml.salary_model import SalaryPredictor

        placement = PlacementPredictor()
        if not placement.load_model():
            metrics = placement.train()
            placement.save_model()
            logger.info(f"  Placement model trained: {metrics.get('accuracy', 0):.1f}% accuracy")
        else:
            logger.info("  Placement model already trained - skipping")

        salary = SalaryPredictor()
        if not salary.load_model():
            metrics = salary.train()
            salary.save_model()
            logger.info(f"  Salary model trained: {metrics.get('r2_score', 0):.1f}% R²")
        else:
            logger.info("  Salary model already trained - skipping")

        return True
    except Exception as e:
        logger.error(f"Model pre-training failed: {e}")
        return False


def verify_directories():
    dirs = [
        "data/datasets", "data/raw", "data/processed",
        "reports", "logs", "src/models/saved_models",
        "static/css", "static/images", "templates"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    logger.info("Directory structure verified - OK")
    return True


def generate_system_info():
    info = {
        "version": config.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "companies": len(config.companies.COMPANIES),
        "technical_skills": len(config.skills.TECHNICAL_SKILLS),
        "soft_skills": len(config.skills.SOFT_SKILLS),
        "domain_skills": len(config.skills.DOMAIN_SKILLS),
    }

    info_path = os.path.join("data", "system_info.json")
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    logger.info(f"System info saved to {info_path}")
    return info


def run_full_init():
    print_banner()
    logger.info("Starting full system initialization...")

    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("spaCy Model", check_spacy),
        ("Directories", verify_directories),
        ("Datasets", generate_datasets),
        ("ML Models", pretrain_models),
    ]

    results = []
    for name, func in steps:
        print(f"\n  [{name}]...", end=" ", flush=True)
        start = time.time()
        try:
            success = func()
            elapsed = time.time() - start
            status = "PASS" if success else "WARN"
            results.append((name, status, f"{elapsed:.1f}s"))
            print(f"{status} ({elapsed:.1f}s)")
        except Exception as e:
            elapsed = time.time() - start
            results.append((name, "FAIL", str(e)[:50]))
            print(f"FAIL ({elapsed:.1f}s): {e}")

    print("\n" + "=" * 60)
    print("  INITIALIZATION SUMMARY")
    print("=" * 60)
    for name, status, detail in results:
        icon = "[OK]" if status == "PASS" else "[!!]" if status == "WARN" else "[XX]"
        print(f"  {icon} {name:<20s} {status:<6s} {detail}")

    all_pass = all(s == "PASS" for _, s, _ in results)
    warn_count = sum(1 for _, s, _ in results if s == "WARN")

    if all_pass:
        print("\n  All checks passed! System is ready.")
    elif warn_count > 0:
        print(f"\n  {warn_count} warning(s). System may have limited functionality.")
    else:
        print("\n  Some checks failed. Please fix the issues above.")

    info = generate_system_info()

    print(f"\n  Version:     {info['version']}")
    print(f"  Companies:   {info['companies']}")
    print(f"  Skills DB:   {info['technical_skills']} technical, "
          f"{info['soft_skills']} soft, {info['domain_skills']} domain")
    print(f"\n  To run: streamlit run app.py")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    setup_logging(log_level="INFO", log_to_file=False, log_to_console=True)
    run_full_init()
