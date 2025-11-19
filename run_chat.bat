@echo off
REM Launcher script for AI Web Reader Chat UI (Windows)

echo 🤖 Démarrage de l'interface de chat AI Web Reader...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ⚠️  Environnement virtuel non trouvé. Création en cours...
    python -m venv venv
)

REM Activate virtual environment
echo 📦 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 📥 Installation des dépendances...
    pip install -r requirements.txt
)

REM Check for .env file
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé!
    echo Vous pouvez configurer l'API key dans l'interface ou créer un fichier .env
    echo.
)

REM Launch Streamlit
echo 🚀 Lancement de l'interface de chat...
echo 📱 L'application s'ouvrira dans votre navigateur
echo 🌐 URL: http://localhost:8501
echo.
echo Appuyez sur Ctrl+C pour arrêter l'application
echo.

streamlit run chat_ui.py
