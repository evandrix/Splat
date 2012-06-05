@echo off

set CONFIGURATION=%1
set PLATFORM=%2
set INPUT=%3
set BITCODE=%4
set BCLIBRARY_UNOPT=%5
set BCLIBRARY=%6

set LLVM_BIN="C:\LLVM\Release\bin"
set CLANG="%LLVM_BIN%\clang"
set LLVM_LINK="%LLVM_BIN%\llvm-link"
set OPT="%LLVM_BIN%\opt"

set CFLAGS=-I.. -I..\Include -I..\PC -D_USRDLL -DPy_BUILD_CORE -DPy_ENABLE_SHARED -DWIN32 -D_WIN32
if "%CONFIGURATION%"=="Debug" set CFLAGS=%CFLAGS% -D_DEBUG
if "%PLATFORM%"=="x64" set CFLAGS=%CFLAGS% -D_WIN64
for /F "delims=;" %%I in ("%INCLUDE%") do set CFLAGS=%CFLAGS% -I"%%I"

%CLANG% -O3 -emit-llvm -c %CFLAGS% %INPUT% -o %BITCODE%
if ERRORLEVEL 1 goto end

%LLVM_LINK% -o %BCLIBRARY_UNOPT% %BITCODE%
if ERRORLEVEL 1 goto end

%OPT% -o %BCLIBRARY% -O3 %BCLIBRARY_UNOPT%

:end
