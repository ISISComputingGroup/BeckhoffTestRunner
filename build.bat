@echo off
setlocal

call find_msc_ver.bat

REM check if msbuild is already in path
call msbuild.exe "/ver"
if %ERRORLEVEL% equ 0 goto :STARTBUILD

call "%VCVARALLDIR%\vcvarsall.bat" x64

:STARTBUILD

REM Building the Beckhoff Builder

call msbuild.exe /p:Configuration=Debug;Platform="Any CPU" /t:clean util_scripts/twinCATAutomationTools/tcSlnFormBuilder/tcSlnFormBuilder.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

call msbuild.exe /p:Configuration=Debug;Platform="Any CPU";RestorePackagesConfig=true /restore util_scripts/twinCATAutomationTools/tcSlnFormBuilder/tcSlnFormBuilder.sln
if %ERRORLEVEL% neq 0 goto :PROBLEM

REM  Use the builder on the PLC solution

call .\util_scripts\twinCATAutomationTools\tcSlnFormBuilder\bin\Debug\tcSlnFormBuilder.exe build --v %MSVC_VER% -s %~dp0\PLC_solution\solution.sln -c "%~dp0\test_config"
if %ERRORLEVEL% neq 0 goto :PROBLEM

GOTO :EOF

:PROBLEM

@echo Beckhoff Build Failed: %ERRORLEVEL%
exit /b 1
