-- AI Resume Analyzer Database Setup Script
-- Run this script in MySQL to create the database before running the application

-- Create the database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS cv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE cv;

-- Note: The tables (user_data and user_feedback) will be created automatically
-- by the application when it runs for the first time.
-- However, if you want to create them manually, uncomment the following:

/*
-- Create user_data table
CREATE TABLE IF NOT EXISTS user_data (
    ID INT NOT NULL AUTO_INCREMENT,
    sec_token varchar(20) NOT NULL,
    ip_add varchar(50) NULL,
    host_name varchar(50) NULL,
    dev_user varchar(50) NULL,
    os_name_ver varchar(50) NULL,
    latlong varchar(50) NULL,
    city varchar(50) NULL,
    state varchar(50) NULL,
    country varchar(50) NULL,
    act_name varchar(50) NOT NULL,
    act_mail varchar(50) NOT NULL,
    act_mob varchar(20) NOT NULL,
    Name varchar(500) NOT NULL,
    Email_ID VARCHAR(500) NOT NULL,
    resume_score VARCHAR(8) NOT NULL,
    Timestamp VARCHAR(50) NOT NULL,
    Page_no VARCHAR(5) NOT NULL,
    Predicted_Field BLOB NOT NULL,
    User_level BLOB NOT NULL,
    Actual_skills BLOB NOT NULL,
    Recommended_skills BLOB NOT NULL,
    Recommended_courses BLOB NOT NULL,
    pdf_name varchar(50) NOT NULL,
    PRIMARY KEY (ID)
);

-- Create user_feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    ID INT NOT NULL AUTO_INCREMENT,
    feed_name varchar(50) NOT NULL,
    feed_email VARCHAR(50) NOT NULL,
    feed_score VARCHAR(5) NOT NULL,
    comments VARCHAR(100) NULL,
    Timestamp VARCHAR(50) NOT NULL,
    PRIMARY KEY (ID)
);
*/

