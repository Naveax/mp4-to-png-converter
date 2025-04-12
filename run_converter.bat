@echo off
echo Installing required packages...
pip install -r requirements.txt
echo.
echo Starting MP4 to PNG Converter...
python mp4_to_png_converter.py
pause 