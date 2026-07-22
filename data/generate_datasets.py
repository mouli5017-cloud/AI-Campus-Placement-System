import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import config


def generate_placement_dataset(n_samples: int = 5000) -> pd.DataFrame:
    np.random.seed(42)

    departments = [
        "Computer Science", "Information Technology",
        "Electronics", "Mechanical", "Civil",
        "Electrical", "Chemical"
    ]
    dept_weights = [0.25, 0.18, 0.18, 0.15, 0.10, 0.08, 0.06]
    genders = ["Male", "Female"]
    college_tiers = ["Tier-1", "Tier-2", "Tier-3"]

    data = {
        "cgpa": np.round(np.random.beta(3, 1.5, n_samples) * 4 + 6, 2),
        "tenth_percentage": np.round(np.random.normal(78, 12, n_samples), 1),
        "twelfth_percentage": np.round(np.random.normal(75, 13, n_samples), 1),
        "backlogs": np.random.choice(
            [0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 4, 5],
            n_samples, p=[0.45, 0.10, 0.10, 0.05, 0.05, 0.05,
                         0.08, 0.05, 0.03, 0.02, 0.01, 0.01]
        ),
        "internships": np.random.choice(
            [0, 0, 0, 1, 1, 1, 2, 2, 3, 4],
            n_samples, p=[0.20, 0.10, 0.10, 0.15, 0.15, 0.10,
                         0.08, 0.05, 0.05, 0.02]
        ),
        "num_technical_skills": np.random.randint(1, 16, n_samples),
        "num_soft_skills": np.random.randint(0, 11, n_samples),
        "num_projects": np.random.randint(0, 9, n_samples),
        "num_certifications": np.random.randint(0, 7, n_samples),
        "experience_years": np.round(
            np.random.exponential(1.0, n_samples), 1
        ),
        "num_programming_languages": np.random.randint(1, 9, n_samples),
        "department": np.random.choice(departments, n_samples, p=dept_weights),
        "gender": np.random.choice(genders, n_samples, p=[0.6, 0.4]),
        "college_tier": np.random.choice(
            college_tiers, n_samples, p=[0.2, 0.4, 0.4]
        ),
    }

    df = pd.DataFrame(data)

    df["tenth_percentage"] = np.clip(df["tenth_percentage"], 40, 99)
    df["twelfth_percentage"] = np.clip(df["twelfth_percentage"], 35, 99)
    df["cgpa"] = np.clip(df["cgpa"], 4.0, 10.0)
    df["experience_years"] = np.clip(df["experience_years"], 0, 5)

    dept_bonus = df["department"].map({
        "Computer Science": 0.12,
        "Information Technology": 0.10,
        "Electronics": 0.04,
        "Mechanical": -0.02,
        "Civil": -0.05,
        "Electrical": -0.01,
        "Chemical": -0.06,
    })

    tier_bonus = df["college_tier"].map({
        "Tier-1": 0.10,
        "Tier-2": 0.02,
        "Tier-3": -0.05,
    })

    placement_prob = (
        0.22 * (df["cgpa"] / 10.0)
        + 0.08 * (df["tenth_percentage"] / 100.0)
        + 0.06 * (df["twelfth_percentage"] / 100.0)
        - 0.12 * (df["backlogs"] / 5.0)
        + 0.10 * (df["internships"] / 4.0)
        + 0.06 * (df["num_technical_skills"] / 15.0)
        + 0.04 * (df["num_soft_skills"] / 10.0)
        + 0.05 * (df["num_projects"] / 8.0)
        + 0.03 * (df["num_certifications"] / 6.0)
        + 0.05 * (df["experience_years"] / 5.0)
        + 0.06 * (df["num_programming_languages"] / 8.0)
        + dept_bonus
        + tier_bonus
        + np.random.normal(0, 0.07, n_samples)
    )

    df["placed"] = (placement_prob > 0.47).astype(int)

    cs_mask = df["department"].isin(["Computer Science", "Information Technology"])
    high_cgpa = df["cgpa"] > 8.0
    df.loc[cs_mask & high_cgpa & (df["internships"] >= 1), "placed"] = 1
    df.loc[(df["cgpa"] < 5.5) & (df["backlogs"] > 3), "placed"] = 0

    return df


def generate_salary_dataset(n_samples: int = 5000) -> pd.DataFrame:
    np.random.seed(42)

    placement_df = generate_placement_dataset(n_samples)
    placed_mask = placement_df["placed"] == 1

    base_salary = (
        2.0
        + 0.9 * placement_df["cgpa"]
        + 0.012 * placement_df["tenth_percentage"]
        + 0.008 * placement_df["twelfth_percentage"]
        - 0.25 * placement_df["backlogs"]
        + 0.6 * placement_df["internships"]
        + 0.12 * placement_df["num_technical_skills"]
        + 0.06 * placement_df["num_soft_skills"]
        + 0.18 * placement_df["num_projects"]
        + 0.12 * placement_df["num_certifications"]
        + 0.5 * placement_df["experience_years"]
        + 0.18 * placement_df["num_programming_languages"]
    )

    dept_mult = placement_df["department"].map({
        "Computer Science": 1.35,
        "Information Technology": 1.25,
        "Electronics": 1.05,
        "Mechanical": 0.85,
        "Civil": 0.75,
        "Electrical": 0.80,
        "Chemical": 0.70,
    })

    tier_mult = placement_df["college_tier"].map({
        "Tier-1": 1.30,
        "Tier-2": 1.00,
        "Tier-3": 0.80,
    })

    salary = (base_salary * dept_mult * tier_mult
              + np.random.normal(0, 0.6, n_samples))

    placement_df["salary_lpa"] = np.round(
        np.where(placed_mask, np.clip(salary, 2.5, 50.0), 0), 2
    )

    return placement_df


def generate_job_postings() -> pd.DataFrame:
    jobs = [
        {
            "company": "TCS", "title": "Software Engineer",
            "skills": ["Java", "Python", "SQL", "Communication"],
            "min_cgpa": 6.0, "min_salary": 3.36, "max_salary": 7.0,
            "location": "Bangalore", "type": "Full-Time"
        },
        {
            "company": "Infosys", "title": "Systems Engineer",
            "skills": ["Java", "Python", "React", "SQL"],
            "min_cgpa": 6.0, "min_salary": 3.60, "max_salary": 6.50,
            "location": "Mysore", "type": "Full-Time"
        },
        {
            "company": "Wipro", "title": "Project Engineer",
            "skills": ["Java", "Python", "Angular", "SQL"],
            "min_cgpa": 6.0, "min_salary": 3.50, "max_salary": 6.00,
            "location": "Pune", "type": "Full-Time"
        },
        {
            "company": "Amazon", "title": "SDE-1",
            "skills": ["Python", "Java", "AWS", "System Design", "DSA"],
            "min_cgpa": 7.0, "min_salary": 12.0, "max_salary": 30.0,
            "location": "Hyderabad", "type": "Full-Time"
        },
        {
            "company": "Google", "title": "Software Engineer L3",
            "skills": ["Python", "Java", "C++", "DSA", "System Design"],
            "min_cgpa": 7.5, "min_salary": 18.0, "max_salary": 45.0,
            "location": "Bangalore", "type": "Full-Time"
        },
        {
            "company": "Microsoft", "title": "Software Engineer",
            "skills": ["C++", "Java", "Python", "DSA", "System Design"],
            "min_cgpa": 7.0, "min_salary": 15.0, "max_salary": 40.0,
            "location": "Hyderabad", "type": "Full-Time"
        },
        {
            "company": "Accenture", "title": "Software Engineer",
            "skills": ["Python", "AWS", "Java", "Communication"],
            "min_cgpa": 6.5, "min_salary": 4.50, "max_salary": 8.00,
            "location": "Pune", "type": "Full-Time"
        },
        {
            "company": "IBM", "title": "Associate Developer",
            "skills": ["Python", "Java", "Cloud Computing", "AI"],
            "min_cgpa": 6.5, "min_salary": 4.00, "max_salary": 12.00,
            "location": "Bangalore", "type": "Full-Time"
        },
        {
            "company": "Capgemini", "title": "Software Engineer",
            "skills": ["Java", "Python", "React", "Docker"],
            "min_cgpa": 6.0, "min_salary": 3.80, "max_salary": 7.00,
            "location": "Mumbai", "type": "Full-Time"
        },
        {
            "company": "Cognizant", "title": "Programmer Analyst",
            "skills": ["Java", "Python", "SQL", "Spring Boot"],
            "min_cgpa": 6.0, "min_salary": 4.00, "max_salary": 7.50,
            "location": "Chennai", "type": "Full-Time"
        },
        {
            "company": "HCL Technologies", "title": "Software Engineer",
            "skills": ["Java", "Python", "Networking", "SQL"],
            "min_cgpa": 6.0, "min_salary": 3.50, "max_salary": 7.00,
            "location": "Noida", "type": "Full-Time"
        },
        {
            "company": "Freshworks", "title": "Software Developer",
            "skills": ["Ruby", "Python", "React", "SQL"],
            "min_cgpa": 6.5, "min_salary": 5.00, "max_salary": 10.00,
            "location": "Chennai", "type": "Full-Time"
        },
        {
            "company": "Zoho", "title": "Software Developer",
            "skills": ["Java", "Python", "JavaScript", "SQL"],
            "min_cgpa": 6.0, "min_salary": 4.50, "max_salary": 9.00,
            "location": "Chennai", "type": "Full-Time"
        },
        {
            "company": "SAP Labs", "title": "Software Developer",
            "skills": ["Java", "Python", "ABAP", "Cloud Computing"],
            "min_cgpa": 7.0, "min_salary": 8.00, "max_salary": 18.00,
            "location": "Bangalore", "type": "Full-Time"
        },
    ]

    return pd.DataFrame(jobs)


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets')
    os.makedirs(output_dir, exist_ok=True)

    print("Generating placement dataset...")
    placement_df = generate_placement_dataset(5000)
    placement_path = os.path.join(output_dir, "placement_dataset.csv")
    placement_df.to_csv(placement_path, index=False)
    print(f"  Saved: {placement_path} ({len(placement_df)} samples)")

    print("\nGenerating salary dataset...")
    salary_df = generate_salary_dataset(5000)
    salary_path = os.path.join(output_dir, "salary_dataset.csv")
    salary_df.to_csv(salary_path, index=False)
    print(f"  Saved: {salary_path} ({len(salary_df)} samples)")

    print("\nGenerating job postings...")
    jobs_df = generate_job_postings()
    jobs_path = os.path.join(output_dir, "job_postings.csv")
    jobs_df.to_csv(jobs_path, index=False)
    print(f"  Saved: {jobs_path} ({len(jobs_df)} jobs)")

    print("\nDataset Generation Complete!")
    print(f"\nPlacement Dataset Shape: {placement_df.shape}")
    print(f"Salary Dataset Shape: {salary_df.shape}")
    print(f"Job Postings Shape: {jobs_df.shape}")
    print(f"\nPlacement Rate: {placement_df['placed'].mean() * 100:.1f}%")
    print(f"Avg Salary (placed): {salary_df[salary_df['salary_lpa'] > 0]['salary_lpa'].mean():.2f} LPA")
