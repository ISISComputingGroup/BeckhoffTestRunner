@echo off
setlocal

call find_msc_ver.bat

if %ERRORLEVEL% neq 0 goto :PROBLEM

REM Start the PLC
call .\util_scripts\twinCATAutomationTools\tcSlnFormBuilder\bin\Debug\tcSlnFormBuilder.exe run -s "%~dp0\PLC_solution\solution.sln" -v %MSVC_VER%

if %ERRORLEVEL% neq 0 goto :PROBLEM

GOTO :EOF

:PROBLEM

@echo Beckhoff Build Failed: %ERRORLEVEL%
exit /b 1
