@echo off
echo ========================================
echo Creating MySQL Database for AI Resume Analyzer
echo ========================================
echo.
echo This script will help you create the database.
echo.
echo IMPORTANT: Make sure MySQL is running and accessible.
echo.

set /p MYSQL_USER="Enter MySQL username (default: root): "
if "%MYSQL_USER%"=="" set MYSQL_USER=root

set /p MYSQL_PASS="Enter MySQL password: "

echo.
echo Creating database 'cv'...
mysql -u %MYSQL_USER% -p%MYSQL_PASS% -e "CREATE DATABASE IF NOT EXISTS cv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create database!
    echo Please check:
    echo 1. MySQL is running
    echo 2. Username and password are correct
    echo 3. User has permission to create databases
    echo.
    echo You can also run the SQL script manually:
    echo   mysql -u %MYSQL_USER% -p < database_setup.sql
    pause
    exit /b 1
) else (
    echo.
    echo Database 'cv' created successfully!
    echo.
    echo You can now run the application using: run.bat
)

pause

