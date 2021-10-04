@echo off

if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
	set "MSVC_VER=VS_2017"
)
if exist "C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build"
	set "MSVC_VER=VS_2017"
)

if exist "C:\Program files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build"
	set "MSVC_VER=VS_2019"
)
if exist "C:\Program files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build" (
    set "VCVARALLDIR=C:\Program files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build"
	set "MSVC_VER=VS_2019"
)
