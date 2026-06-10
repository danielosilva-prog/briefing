@echo off
setlocal

set "UF=%~1"
if "%UF%"=="" (
  echo Uso: gera_anexos_briefing.bat UF [CAMINHO_CSV]
  echo Exemplo: gera_anexos_briefing.bat RJ
  exit /b 1
)

set "INPUT_FILE=%~2"
if "%INPUT_FILE%"=="" (
  set "INPUT_FILE=reports/ANEXOS-BRIEFINGS/data/Anexos-briefing.csv"
)

cd /d "%~dp0..\.."
set "PYTHONUTF8=1"

uv run schoolreport generate ANEXOS-BRIEFINGS uf=%UF% secretaria=SETEC input_file=%INPUT_FILE% --output output/anexo-setec-%UF%.pdf
if errorlevel 1 exit /b %errorlevel%

uv run schoolreport generate ANEXOS-BRIEFINGS uf=%UF% secretaria=SESU input_file=%INPUT_FILE% --output output/anexo-sesu-%UF%.pdf
if errorlevel 1 exit /b %errorlevel%

echo.
echo Anexos gerados em output:
echo - output/anexo-setec-%UF%.pdf
echo - output/anexo-sesu-%UF%.pdf
