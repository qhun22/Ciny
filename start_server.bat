@echo off
echo ============================================
echo Starting Django Server for Shop Project
echo ============================================
echo.
cd /d %~dp0
echo Current directory: %cd%
echo.
echo Step 1: Checking Django...
python -c "import django; print(f'Django version: {django.get_version()}')"
echo.
echo Step 2: Starting server on port 8000...
echo.
python manage.py runserver 0.0.0.0:8000
echo.
echo Server stopped.
pause

