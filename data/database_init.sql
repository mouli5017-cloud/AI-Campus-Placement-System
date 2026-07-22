-- ============================================================
-- AI Campus Placement Prediction & Resume Screening System
-- Database Schema & Initialization Script
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_placement_ai
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE campus_placement_ai;

-- ============================================================
-- Users Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'placement_officer') NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB;

-- ============================================================
-- Student Profiles Table
-- ============================================================
CREATE TABLE IF NOT EXISTS student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_of_study INT NOT NULL,
    cgpa DECIMAL(4,2) NOT NULL,
    tenth_percentage DECIMAL(5,2),
    twelfth_percentage DECIMAL(5,2),
    backlogs INT DEFAULT 0,
    gender VARCHAR(20),
    date_of_birth VARCHAR(20),
    phone VARCHAR(20),
    address TEXT,
    programming_languages JSON,
    technical_skills JSON,
    soft_skills JSON,
    certifications JSON,
    projects JSON,
    internships INT DEFAULT 0,
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    placement_status ENUM('not_placed', 'placed', 'in_process', 'offer_received') DEFAULT 'not_placed',
    target_salary_lpa DECIMAL(5,2) DEFAULT 4.00,
    preferred_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_roll (roll_number),
    INDEX idx_department (department),
    INDEX idx_cgpa (cgpa)
) ENGINE=InnoDB;

-- ============================================================
-- Resumes Table
-- ============================================================
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    parsed_text TEXT,
    extracted_skills JSON,
    ats_score DECIMAL(5,2),
    experience_years DECIMAL(4,1) DEFAULT 0.0,
    education_details JSON,
    projects_extracted JSON,
    certifications_extracted JSON,
    raw_sections JSON,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ats_score (ats_score)
) ENGINE=InnoDB;

-- ============================================================
-- Job Postings Table
-- ============================================================
CREATE TABLE IF NOT EXISTS job_postings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    description TEXT,
    required_skills JSON,
    min_cgpa DECIMAL(4,2) DEFAULT 6.00,
    min_salary_lpa DECIMAL(5,2),
    max_salary_lpa DECIMAL(5,2),
    location VARCHAR(100),
    job_type VARCHAR(50) DEFAULT 'Full-Time',
    experience_required DECIMAL(4,1) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    application_deadline DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company (company_name),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- ============================================================
-- Job Applications Table
-- ============================================================
CREATE TABLE IF NOT EXISTS job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    match_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_job (job_id)
) ENGINE=InnoDB;

-- ============================================================
-- Prediction History Table
-- ============================================================
CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    input_features JSON,
    prediction_result JSON,
    confidence_score DECIMAL(5,2),
    model_version VARCHAR(50),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_type (prediction_type)
) ENGINE=InnoDB;

-- ============================================================
-- Learning Recommendations Table
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_gap VARCHAR(100) NOT NULL,
    course_name VARCHAR(300) NOT NULL,
    course_url VARCHAR(500),
    platform VARCHAR(100),
    difficulty_level VARCHAR(50),
    estimated_hours INT,
    description TEXT,
    relevance_score DECIMAL(5,2) DEFAULT 0.00,
    INDEX idx_skill (skill_gap)
) ENGINE=InnoDB;

-- ============================================================
-- Email Logs Table
-- ============================================================
CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(300) NOT NULL,
    body TEXT,
    email_type VARCHAR(50),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent',
    INDEX idx_recipient (recipient_email),
    INDEX idx_type (email_type)
) ENGINE=InnoDB;

-- ============================================================
-- Analytics Logs Table
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSON,
    user_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- ============================================================
-- Seed Data: Admin User
-- ============================================================
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@campus.edu', '$2b$12$LJ3m4ys4I3g2S9k1Y1z8Xe0K8F3hQ5vN7pR1tY6wA9bC2dE4fG5hI', 'admin')
ON DUPLICATE KEY UPDATE username = username;

-- ============================================================
-- Seed Data: Placement Officer
-- ============================================================
INSERT INTO users (username, email, password_hash, role)
VALUES ('placement_cell', 'placement@campus.edu', '$2b$12$LJ3m4ys4I3g2S9k1Y1z8Xe0K8F3hQ5vN7pR1tY6wA9bC2dE4fG5hI', 'placement_officer')
ON DUPLICATE KEY UPDATE username = username;

-- ============================================================
-- Seed Data: Sample Job Postings
-- ============================================================
INSERT INTO job_postings (company_name, job_title, description, required_skills, min_cgpa, min_salary_lpa, max_salary_lpa, location)
VALUES
('TCS', 'Software Engineer', 'Full-stack development role at TCS', '["Java", "Python", "SQL", "Communication"]', 6.00, 3.36, 7.00, 'Bangalore'),
('Infosys', 'Systems Engineer', 'Software development at Infosys', '["Java", "Python", "React", "SQL"]', 6.00, 3.60, 6.50, 'Mysore'),
('Amazon', 'Software Development Engineer', 'SDE role at Amazon', '["Python", "Java", "AWS", "System Design", "DSA"]', 7.00, 12.00, 30.00, 'Hyderabad'),
('Google', 'Software Engineer', 'SWE role at Google', '["Python", "Java", "C++", "DSA", "System Design"]', 7.50, 18.00, 45.00, 'Bangalore'),
('Microsoft', 'Software Engineer', 'SDE role at Microsoft', '["C++", "Java", "Python", "DSA", "System Design"]', 7.00, 15.00, 40.00, 'Hyderabad'),
('Wipro', 'Project Engineer', 'IT services at Wipro', '["Java", "Python", "Angular", "SQL"]', 6.00, 3.50, 6.00, 'Pune'),
('Accenture', 'Software Engineer', 'Consulting role at Accenture', '["Python", "AWS", "Java", "Communication"]', 6.50, 4.50, 8.00, 'Pune'),
('IBM', 'Associate Software Engineer', 'Development role at IBM', '["Python", "Java", "Cloud Computing", "AI"]', 6.50, 4.00, 12.00, 'Bangalore')
ON DUPLICATE KEY UPDATE company_name = company_name;

-- ============================================================
-- Seed Data: Learning Recommendations
-- ============================================================
INSERT INTO learning_recommendations (skill_gap, course_name, platform, difficulty_level, estimated_hours, relevance_score)
VALUES
('Python', 'Python for Everybody Specialization', 'Coursera', 'Beginner', 40, 95.00),
('Java', 'Java Programming Masterclass', 'Udemy', 'Intermediate', 80, 90.00),
('React', 'React - The Complete Guide', 'Udemy', 'Intermediate', 48, 88.00),
('Machine Learning', 'Machine Learning by Andrew Ng', 'Coursera', 'Intermediate', 56, 92.00),
('AWS', 'AWS Cloud Practitioner Essentials', 'AWS', 'Beginner', 40, 85.00),
('Docker', 'Docker & Kubernetes: The Practical Guide', 'Udemy', 'Intermediate', 24, 82.00),
('SQL', 'The Complete SQL Bootcamp', 'Udemy', 'Beginner', 30, 87.00),
('Data Structures', 'Data Structures & Algorithms Bootcamp', 'Udemy', 'Intermediate', 100, 93.00),
('System Design', 'System Design Interview Course', 'Educative', 'Advanced', 30, 80.00),
('Git', 'Git & GitHub Crash Course', 'Udemy', 'Beginner', 8, 75.00)
ON DUPLICATE KEY UPDATE skill_gap = skill_gap;

SELECT 'Database initialization complete!' AS status;
