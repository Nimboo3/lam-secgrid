@echo off
echo Setting up demonstration environment...
echo.

REM Clear any existing demo results
if exist results\demo_clean.csv del results\demo_clean.csv
if exist results\demo_attacks rmdir /s /q results\demo_attacks
if exist results\demo_defenses rmdir /s /q results\demo_defenses

echo Clean slate prepared for demonstration.
echo.
echo Ready to run demo commands from DEMO_GUIDE.md
echo.
echo QUICK TEST - Verifying all components work:
C:/Projects/lam-secgrid/venv/Scripts/python.exe -c "from env import GridWorld; from policies import rule_based_policy; import attacks; import defenses; print('✅ All imports successful - ready for demo!')"

pause
