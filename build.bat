@echo off
setlocal

if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
)
if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build"
)

REM check if msbuild is already in path
call msbuild.exe "/ver"
if %ERRORLEVEL% equ 0 goto :STARTBUILD

call "%VCVARALLDIR%\vcvarsall.bat" x64

:STARTBUILD

REM Building the Beckhoff Builder

call msbuild.exe /p:Configuration=Release;Platform=x64 /t:clean util_scripts/AutomationTools/AutomationTools.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

call msbuild.exe /p:Configuration=Release;Platform=x64 util_scripts/AutomationTools/AutomationTools.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

call msbuild.exe /p:Configuration=Debug;Platform="Any CPU" /t:clean util_scripts/twinCATAutomationTools/tcSlnFormBuilder/tcSlnFormBuilder.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

call msbuild.exe /p:Configuration=Debug;Platform="Any CPU" util_scripts/twinCATAutomationTools/tcSlnFormBuilder/tcSlnFormBuilder.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

REM  Use the builder on the PLC solution

call .\util_scripts\twinCATAutomationTools\tcSlnFormBuilder\bin\Debug\tcSlnFormBuilder.exe VS_2017 %~dp0\PLC_solution\solution.sln "%~dp0\test_config"
REM call .\util_scripts\twinCATAutomationTools\tcSlnFormBuilder\bin\Debug\tcSlnFormBuilder.exe VS_2017 C:\non_ibex_dev\beckhoff\collab_project\solution.sln "%~dp0\test_config"
if %ERRORLEVEL% neq 0 goto :PROBLEM

GOTO :EOF

:PROBLEM

@echo Beckhoff Build Failed: %ERRORLEVEL%
exit /b 1
