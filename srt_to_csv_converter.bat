@echo off
chcp 65001 >nul
echo ============================================================
echo SRT → CSV 辞書変換ツール
echo ============================================================
echo.
echo 使い方:
echo 1. 英語のSRTファイルをドラッグ&ドロップ
echo 2. Enterキーを押す
echo 3. 日本語のSRTファイルをドラッグ&ドロップ
echo 4. Enterキーを押す
echo.
echo ============================================================
echo.

set /p english_file="英語SRTファイルをドラッグ&ドロップしてください: "
set english_file=%english_file:"=%

if not exist "%english_file%" (
    echo エラー: 英語ファイルが見つかりません。
    pause
    exit /b
)

set /p japanese_file="日本語SRTファイルをドラッグ&ドロップしてください: "
set japanese_file=%japanese_file:"=%

if not exist "%japanese_file%" (
    echo エラー: 日本語ファイルが見つかりません。
    pause
    exit /b
)

echo.
echo 処理中...
echo.

for %%F in ("%english_file%") do set "basename=%%~nF"
set "output_csv=%basename%_dictionary.csv"

python create_dictionary.py "%english_file%" "%japanese_file%" "%output_csv%"

if exist "%output_csv%" (
    echo.
    echo ============================================================
    echo 完成しました！
    echo ============================================================
    echo 出力ファイル: %output_csv%
    echo.
    echo このCSVファイルをStreamlitアプリにアップロードできます。
    echo ============================================================
) else (
    echo.
    echo エラー: CSVの生成に失敗しました。
)

echo.
pause

