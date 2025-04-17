@echo off
echo Setting up EMA Heikin Ashi Strategy...

:: Remove existing virtual environment if exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

:: Create fresh virtual environment
echo Creating new virtual environment...
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Create necessary directories
echo Creating necessary directories...
if not exist "data\market_data" mkdir data\market_data
if not exist "data\results" mkdir data\results
if not exist "logs" mkdir logs

echo.
echo Setup complete!
echo.
echo Please place your NIFTY_1min.csv file in the data\market_data folder.
echo Then run the strategy using run.bat or 'python main.py --visualize'
echo.
pause