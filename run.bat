@echo off
setlocal

@REM if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build" (
@REM     set "VCVARALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
@REM )
@REM if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build" (
@REM     set "VCVARALLDIR=C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build"
@REM )

@REM REM check if msbuild is already in path
@REM call msbuild.exe "/ver"
@REM if %ERRORLEVEL% equ 0 goto :STARTBUILD

@REM call "%VCVARALLDIR%\vcvarsall.bat" x64

@REM :STARTBUILD

REM Building the Beckhoff Builder
REM call msbuild.exe /p:Configuration=Release;Platform=x64 util_scripts/AutomationTools/AutomationTools.sln

if %ERRORLEVEL% neq 0 goto :PROBLEM

REM Start the PLC
call .\util_scripts\twinCATAutomationTools\tcSlnFormBuilder\bin\Debug\tcSlnFormBuilder.exe run -s "%~dp0\PLC_solution\solution.sln"

if %ERRORLEVEL% neq 0 goto :PROBLEM

GOTO :EOF

:PROBLEM

@echo Beckhoff Build Failed: %ERRORLEVEL%
exit /b 1
