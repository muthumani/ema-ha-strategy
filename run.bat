@echo off
echo Running EMA Heikin Ashi Strategy...

:: Check if virtual environment exists, if not create it
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: Create necessary directories
if not exist "data\market_data" mkdir data\market_data
if not exist "data\results" mkdir data\results
if not exist "logs" mkdir logs

:: Check if config file exists
if not exist "config\config.yaml" (
    echo WARNING: config.yaml file not found in config directory
    pause
    exit
)

:: Check if data file exists
if not exist "data\market_data\NIFTY_1min.csv" (
    echo WARNING: Please place your NIFTY_1min.csv file in data\market_data folder
    pause
    exit
)

:: Parse command line arguments
set ARGS=
:parse
if "%~1"=="" goto :execute
set ARGS=%ARGS% %1
shift
goto :parse

:execute
:: Run the main script with arguments
echo Running strategy...
python main.py %ARGS%

:: Keep window open to see results
pause
