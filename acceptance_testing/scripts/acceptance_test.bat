@echo off
REM acceptance_test.bat - Windows batch file for running acceptance tests

echo ======================================================
echo    EMA-HA Strategy Acceptance Testing Suite
echo    %date% %time%
echo ======================================================

REM Create logs directory
mkdir logs 2>nul

REM Set log file
set LOG_FILE=logs\acceptance_test_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

REM Set results file
set RESULTS_FILE=logs\test_results_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.csv
set RESULTS_FILE=%RESULTS_FILE: =0%

REM Initialize results file
echo Test ID,Description,Status,Duration,Notes > %RESULTS_FILE%

echo Running Acceptance Tests...
echo Logging to: %LOG_FILE%
echo Results will be saved to: %RESULTS_FILE%

REM Section 1: Unit Tests
echo.
echo Section 1: Unit Tests
call :run_test "UT-001" "Run all unit tests" "pytest tests/unit/ -v"
call :run_test "UT-002" "Run unit tests with coverage" "pytest tests/unit/ --cov=. --cov-report=term-missing"

REM Section 2: Integration Tests
echo.
echo Section 2: Integration Tests
call :run_test "IT-001" "Run all integration tests" "pytest tests/integration/ -v"
call :run_test "IT-002" "Run integration tests with coverage" "pytest tests/integration/ --cov=. --cov-report=term-missing"

REM Section 3: Basic Functionality Tests
echo.
echo Section 3: Basic Functionality Tests
call :run_test "F-001" "Run single backtest with default settings" "python main.py"
call :run_test "F-002" "Run with specific trading mode (BUY)" "python main.py --mode BUY"
call :run_test "F-003" "Run with specific trading mode (SELL)" "python main.py --mode SELL"
call :run_test "F-004" "Run with specific trading mode (SWING)" "python main.py --mode SWING"
call :run_test "F-005" "Run with specific candle pattern (2)" "python main.py --pattern 2"
call :run_test "F-006" "Run with specific candle pattern (3)" "python main.py --pattern 3"
call :run_test "F-007" "Run with specific candle pattern (None)" "python main.py --pattern None"

REM Section 4: Comparative Analysis Tests
echo.
echo Section 4: Comparative Analysis Tests
call :run_test "C-001" "Compare all trading modes" "python main.py --compare modes"
call :run_test "C-002" "Compare all candle patterns" "python main.py --compare patterns"
call :run_test "C-003" "Run all combinations" "python main.py --all"

REM Section 5: Report Generation Tests
echo.
echo Section 5: Report Generation Tests
call :run_test "R-001" "Generate Excel report" "python main.py --report"
call :run_test "R-002" "Generate consolidated report" "python main.py --all --report"

REM Section 6: Performance Testing
echo.
echo Section 6: Performance Testing
call :run_test "P-001" "Run single backtest performance" "python main.py"
call :run_test "P-002" "Run all combinations performance" "python main.py --all"

REM Section 7: Cross-Validation Tests
echo.
echo Section 7: Cross-Validation Tests
call :run_test "V-001" "Run cross-validation" "python main.py --validate"
call :run_test "V-002" "Run deterministic mode" "python main.py --deterministic --seed 42"
call :run_test "V-003" "Run sequential mode" "python main.py --sequential"

REM Section 8: Error Handling Tests
echo.
echo Section 8: Error Handling Tests
call :run_test "E-001" "Invalid configuration file" "python main.py --config nonexistent.yaml"
call :run_test "E-002" "Missing market data" "python main.py --data nonexistent.csv"
call :run_test "E-003" "Invalid command line arguments" "python main.py --invalid-argument"

REM Generate summary report
echo.
echo ======================================================
echo    Acceptance Test Summary
echo ======================================================

REM Count passed and total tests
findstr /C:"PASS" %RESULTS_FILE% > nul
set /A pass_count=%ERRORLEVEL%
findstr /C:"Test ID" %RESULTS_FILE% > nul
set /A total_count=%ERRORLEVEL%
set /A pass_percentage=pass_count*100/total_count

echo Total Tests: %total_count%
echo Passed Tests: %pass_count%
echo Failed Tests: %total_count - %pass_count%
echo Pass Percentage: %pass_percentage%%%

if %pass_percentage% GEQ 95 (
    echo ACCEPTANCE CRITERIA MET: %pass_percentage%%% of tests passed
    exit /b 0
) else (
    echo ACCEPTANCE CRITERIA NOT MET: Only %pass_percentage%%% of tests passed (95%% required)
    exit /b 1
)

:run_test
set test_id=%~1
set description=%~2
set command=%~3
set expected_exit_code=0

echo Running Test %test_id%: %description%
echo Command: %command% >> %LOG_FILE%

REM Measure execution time
set start_time=%time%

REM Run the command and capture output
set output_file=logs\%test_id%_output.log
%command% > %output_file% 2>&1
set exit_code=%ERRORLEVEL%

REM Calculate duration (simplified)
set end_time=%time%
set duration=%end_time%

REM Check if test passed
if %exit_code% EQU %expected_exit_code% (
    set status=PASS
    echo [✓] Test %test_id% passed (%duration%)
) else (
    set status=FAIL
    echo [✗] Test %test_id% failed (%duration%)
    echo   Expected exit code: %expected_exit_code%, Actual: %exit_code%
)

REM Record result in CSV
echo %test_id%,"%description%",%status%,%duration%,"Exit code: %exit_code%" >> %RESULTS_FILE%

exit /b %exit_code%
