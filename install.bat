@echo off
REM Script d'installation pour AI Web Reader (Windows)
setlocal enabledelayedexpansion

echo ================================================
echo   Installation de AI Web Reader
echo ================================================
echo.

REM Vérifier Python
echo Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Installez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detecte

REM Créer environnement virtuel
if not exist "venv" (
    echo.
    echo Creation de l'environnement virtuel...
    python -m venv venv
    echo [OK] Environnement virtuel cree
) else (
    echo [INFO] Environnement virtuel existant detecte
)

REM Activer l'environnement virtuel
echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Mise à jour de pip
echo.
echo Mise a jour de pip...
python -m pip install --upgrade pip --quiet

REM Installer ChromaDB
echo.
echo Installation de ChromaDB (peut prendre quelques minutes)...
python -c "import chromadb" 2>nul
if errorlevel 1 (
    echo    Telechargement de ChromaDB avec wheels pre-compilees...
    pip install --only-binary=:all: chromadb==0.5.3 --quiet
    if errorlevel 1 (
        echo [WARN] Installation avec wheels echouee, tentative normale...
        pip install chromadb==0.5.3
    )
    echo [OK] ChromaDB installe
) else (
    echo [OK] ChromaDB deja installe
)

REM Installer les autres dépendances
echo.
echo Installation des autres dependances...
pip install beautifulsoup4==4.12.3 --quiet
pip install requests==2.31.0 --quiet
pip install anthropic==0.39.0 --quiet
pip install fastapi==0.109.0 --quiet
pip install uvicorn==0.27.0 --quiet
pip install pydantic==2.5.3 --quiet
pip install pydantic-settings==2.1.0 --quiet
pip install python-dotenv==1.0.0 --quiet
pip install apscheduler==3.10.4 --quiet
pip install lxml==5.1.0 --quiet
pip install aiohttp==3.9.1 --quiet
pip install streamlit==1.29.0 --quiet
pip install watchdog==3.0.0 --quiet

echo [OK] Toutes les dependances installees

REM Vérification
echo.
echo Verification de l'installation...

python -c "import chromadb; import anthropic; import streamlit; from bs4 import BeautifulSoup; import fastapi; print('[OK] Tous les modules importes avec succes!')"
if errorlevel 1 (
    echo.
    echo ================================================
    echo   [ERREUR] Installation echouee
    echo ================================================
    echo.
    echo Consultez INSTALLATION.md pour le depannage
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Installation terminee avec succes!
echo ================================================
echo.
echo Prochaines etapes:
echo.
echo 1. Configurez votre cle API:
echo    copy .env.example .env
echo    notepad .env  (Editez avec votre cle API)
echo.
echo 2. Lancez l'interface de chat:
echo    run_chat.bat
echo.
echo 3. Ou lancez l'API:
echo    venv\Scripts\activate
echo    python main.py
echo.
pause
