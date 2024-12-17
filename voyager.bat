@echo off
setlocal EnableDelayedExpansion

:: Check for verbose flag
set "VERBOSE="
if "%2"=="--verbose" set "VERBOSE=1"
if "%1"=="--verbose" set "VERBOSE=1"

:: Set redirection based on verbose flag
if not defined VERBOSE (
    set "QUIET_REDIRECT=>nul"
    set "NPM_QUIET=--quiet"
) else (
    set "QUIET_REDIRECT="
    set "NPM_QUIET="
)

:: Check parameters
if "%1"=="install" (
    goto :install
) else if "%1"=="" (
    goto :run
) else if "%1"=="--verbose" (
    if "%2"=="install" (
        goto :install
    ) else (
        goto :usage
    )
) else (
    :usage
    echo Usage: voyager.bat [install] [--verbose]
    echo   install   : Install or reinstall the application
    echo   --verbose : Show detailed installation output
    echo   no args  : Run the application
    exit /b 1
)

:run
:: Check if environment exists
if not exist venv (
    echo Virtual environment not found.
    echo Please run 'voyager.bat -install' first to set up the application.
    exit /b 1
)

:: Activate environment and run
echo Starting Voyager...
call .\venv\Scripts\activate || (
    echo Error: Failed to activate virtual environment
    exit /b 1
)
python . || (
    echo Error: Failed to start application
    exit /b 1
)
exit /b 0

:install
echo Starting installation...

:: Check for Python 3.10
echo Checking Python version...
set "PYTHON_CMD="

:: Try python3.10 command first
python3.10 --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PYTHON_CMD=python3.10"
) else (
    :: Try py launcher with -3.10 flag
    py -3.10 --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_CMD=py -3.10"
    )
)

:: Check if we found Python 3.10
if not defined PYTHON_CMD (
    echo Python 3.10.x is not installed or not available. Please install Python 3.10.x.
    exit /b 1
)

:: Get the exact version
for /f "tokens=2 delims= " %%v in ('!PYTHON_CMD! --version 2^>nul') do (
    set PYTHON_VERSION=%%v
)
echo Found Python version %PYTHON_VERSION%

:: Check for Node.js
echo Checking Node.js version...
for /f "delims=" %%i in ('node -v 2^>nul') do set "NODE_VERSION=%%i"
if not defined NODE_VERSION (
    echo Node.js is not installed. Please install Node.js.
    exit /b 1
)
set "NODE_VERSION=!NODE_VERSION:v=!"
echo Found Node.js version !NODE_VERSION!
:: Parse the major version number
for /f "tokens=1 delims=." %%a in ("!NODE_VERSION!") do (
    if %%a LSS 10 (
        echo Node.js version is lower than 10. Please install Node.js 10 or later.
        exit /b 1
    )
)

:: Deactivate any existing virtual environment
if defined VIRTUAL_ENV (
    call deactivate
)

:: Remove existing Python virtual environment if it exists
if exist venv (
    echo Removing existing virtual environment...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq venv*" >nul 2>&1
    timeout /t 2 /nobreak >nul
    rmdir /S /Q venv 2>nul || (
        echo Error: Could not remove existing virtual environment. Please close any programs using it and try again.
        exit /b 1
    )
)

:: Create a Python virtual environment using Python 3.10
echo Creating new virtual environment...
!PYTHON_CMD! -m venv venv || (
    echo Error: Failed to create virtual environment
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate || (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

:: Install dependencies in editable mode
echo Installing Python dependencies...
pip install -e . %QUIET_REDIRECT% 2>&1 || (
    echo Error: Failed to install Python dependencies
    exit /b 1
)

:: Change to the mineflayer environment directory
echo Setting up Mineflayer environment...
pushd voyager\env\mineflayer || (
    echo Error: Could not find mineflayer directory
    exit /b 1
)

:: Install npx globally and necessary Node.js dependencies
echo Installing Node.js dependencies...
call npm install -g npx %NPM_QUIET% %QUIET_REDIRECT% 2>&1 || (
    echo Error: Failed to install npx
    exit /b 1
)
call npm install %NPM_QUIET% %QUIET_REDIRECT% 2>&1 || (
    echo Error: Failed to install Node.js dependencies
    exit /b 1
)

:: Change to the mineflayer-collectblock directory and compile
echo Setting up mineflayer-collectblock...
cd mineflayer-collectblock || (
    echo Error: Could not find mineflayer-collectblock directory
    exit /b 1
)
if defined VERBOSE (
    call npx tsc || (
        echo Error: TypeScript compilation failed
        exit /b 1
    )
) else (
    call npx tsc >nul || (
        echo Error: TypeScript compilation failed. Run with --verbose to see detailed errors.
        exit /b 1
    )
)

:: Return to the mineflayer directory
cd ..
call npm install %NPM_QUIET% %QUIET_REDIRECT% || (
    echo Error: Failed to install remaining Node.js dependencies
    exit /b 1
)

:: Return to the previous directory
popd

echo Installation completed successfully!
echo Run 'voyager.bat' without parameters to start the application.
exit /b 0

endlocal