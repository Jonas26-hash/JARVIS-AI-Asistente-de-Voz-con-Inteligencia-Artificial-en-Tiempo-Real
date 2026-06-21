@echo off
setlocal
set "ROOT=%~dp0.."
pushd "%ROOT%"

set "PYW=%ROOT%\.venv\Scripts\pythonw.exe"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "BOT=%ROOT%\telegram_bot.py"

if exist "%PYW%" (
    start "" "%PYW%" "%BOT%" & goto :done
)
if exist "%PY%" (
    start "" /B "%PY%" "%BOT%" & goto :done
)

echo JARVIS Telegram: no se encontro Python.
pause
:done
popd
endlocal
