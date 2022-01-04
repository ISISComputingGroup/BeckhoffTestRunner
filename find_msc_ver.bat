rem @echo off

for %%j in ( 2017 2019 ) do (
    for %%i in ( Professional Community Enterprise ) do (
        if exist "C:\Program files (x86)\Microsoft Visual Studio\%%j\%%i\VC\Auxiliary\Build" (
            set "VCVARALLDIR=C:\Program files (x86)\Microsoft Visual Studio\%%j\%%i\VC\Auxiliary\Build"
	        set "MSVC_VER=VS_%%j"
        )
    )
)
