@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo.
echo Available commands:
echo   python inspect_dataset.py  - Inspect the dataset
echo   python ranker.py           - Run the weekend ranker
echo.
echo To deactivate: deactivate
echo.

cmd /k