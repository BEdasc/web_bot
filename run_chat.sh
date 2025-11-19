#!/bin/bash
# Launcher script for AI Web Reader Chat UI

echo "🤖 Démarrage de l'interface de chat AI Web Reader..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activation de l'environnement virtuel..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📥 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé!"
    echo "Vous pouvez configurer l'API key dans l'interface ou créer un fichier .env"
    echo ""
fi

# Launch Streamlit
echo "🚀 Lancement de l'interface de chat..."
echo "📱 L'application s'ouvrira dans votre navigateur"
echo "🌐 URL: http://localhost:8501"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

streamlit run chat_ui.py
