@echo off
cd /d "%~dp0"
echo ================================================
echo 翻訳フレーズ辞書アプリを起動しています...
echo ================================================
echo.
python -m streamlit run app.py
pause

