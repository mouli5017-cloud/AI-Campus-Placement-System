"""
Setup and Run Script for Campus Placement AI System
Run this file to install dependencies and launch the application.
"""
import subprocess
import sys
import os


def install_dependencies():
    print("=" * 60)
    print("  AI Campus Placement System - Setup")
    print("=" * 60)

    print("\n[1/4] Installing Python packages...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("  -> All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"  -> Error installing packages: {e}")
        return False

    print("\n[2/4] Downloading spaCy English model...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("  -> spaCy model downloaded!")
    except subprocess.CalledProcessError:
        print("  -> Warning: spaCy model download failed. Some NLP features may be limited.")

    print("\n[3/4] Generating datasets...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from data.generate_datasets import (
            generate_placement_dataset,
            generate_salary_dataset,
            generate_job_postings
        )

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "datasets")
        os.makedirs(output_dir, exist_ok=True)

        df = generate_placement_dataset(5000)
        df.to_csv(os.path.join(output_dir, "placement_dataset.csv"), index=False)
        print(f"  -> Placement dataset: {len(df)} samples")

        df2 = generate_salary_dataset(5000)
        df2.to_csv(os.path.join(output_dir, "salary_dataset.csv"), index=False)
        print(f"  -> Salary dataset: {len(df2)} samples")

        df3 = generate_job_postings()
        df3.to_csv(os.path.join(output_dir, "job_postings.csv"), index=False)
        print(f"  -> Job postings: {len(df3)} records")
    except Exception as e:
        print(f"  -> Warning: Dataset generation had issues: {e}")

    print("\n[4/4] Creating model directory...")
    model_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "src", "models", "saved_models"
    )
    os.makedirs(model_dir, exist_ok=True)
    print("  -> Model directory ready!")

    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    return True


def run_app():
    print("\nLaunching Streamlit application...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the server.\n")

    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", app_path,
         "--server.headless", "true"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )


def run_tests():
    print("\nRunning unit tests...")
    test_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "tests", "test_models.py"
    )
    subprocess.run([sys.executable, "-m", "pytest", test_path, "-v"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "setup":
            install_dependencies()
        elif command == "run":
            run_app()
        elif command == "test":
            run_tests()
        elif command == "all":
            if install_dependencies():
                run_app()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python setup.py [setup|run|test|all]")
    else:
        print("Usage: python setup.py [setup|run|test|all]")
        print("")
        print("  setup  - Install dependencies and generate data")
        print("  run    - Launch the Streamlit application")
        print("  test   - Run unit tests")
        print("  all    - Setup and run")
