#!/bin/bash
# Script d'installation intelligent pour AI Web Reader
# Gère l'installation de ChromaDB avec wheels pré-compilées

set -e  # Arrêter en cas d'erreur

echo "🤖 Installation de AI Web Reader"
echo "================================"
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier Python
echo "📋 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} détecté"

# Vérifier/Créer environnement virtuel
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Environnement virtuel créé"
else
    echo -e "${YELLOW}⚠${NC}  Environnement virtuel existant détecté"
fi

# Activer l'environnement virtuel
echo ""
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mise à jour de pip
echo ""
echo "⬆️  Mise à jour de pip..."
python -m pip install --upgrade pip --quiet

# Installation de ChromaDB en premier (avec wheel binaire)
echo ""
echo "🔍 Installation de ChromaDB (ceci peut prendre quelques minutes)..."
if python -c "import chromadb" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} ChromaDB déjà installé"
else
    echo "   Téléchargement de ChromaDB avec wheels pré-compilées..."
    # Forcer l'utilisation de wheels binaires - version 0.5.20 pour Python 3.12+
    pip install --only-binary=:all: chromadb==0.5.20 --quiet || {
        echo -e "${YELLOW}⚠${NC}  Installation avec wheels échouée, tentative normale..."
        pip install chromadb==0.5.20
    }
    echo -e "${GREEN}✓${NC} ChromaDB installé"
fi

# Installation des autres dépendances
echo ""
echo "📚 Installation des autres dépendances..."

# Liste des paquets à installer (sans ChromaDB)
PACKAGES=(
    "beautifulsoup4==4.12.3"
    "requests==2.31.0"
    "anthropic==0.40.0"
    "fastapi==0.109.0"
    "uvicorn==0.27.0"
    "pydantic==2.5.3"
    "pydantic-settings==2.1.0"
    "python-dotenv==1.0.0"
    "apscheduler==3.10.4"
    "lxml==5.1.0"
    "aiohttp==3.9.1"
    "streamlit==1.29.0"
    "watchdog==3.0.0"
)

for package in "${PACKAGES[@]}"; do
    package_name=$(echo $package | cut -d'=' -f1)
    if python -c "import ${package_name//-/_}" 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} ${package_name}"
    else
        echo -e "   📥 ${package_name}..."
        pip install "$package" --quiet
    fi
done

echo -e "${GREEN}✓${NC} Toutes les dépendances installées"

# Vérification finale
echo ""
echo "🧪 Vérification de l'installation..."

python3 << 'EOF'
import sys
errors = []

try:
    import chromadb
    print("   ✓ chromadb")
except ImportError as e:
    errors.append(f"chromadb: {e}")
    print(f"   ✗ chromadb")

try:
    import anthropic
    print("   ✓ anthropic")
except ImportError as e:
    errors.append(f"anthropic: {e}")
    print(f"   ✗ anthropic")

try:
    import streamlit
    print("   ✓ streamlit")
except ImportError as e:
    errors.append(f"streamlit: {e}")
    print(f"   ✗ streamlit")

try:
    from bs4 import BeautifulSoup
    print("   ✓ beautifulsoup4")
except ImportError as e:
    errors.append(f"beautifulsoup4: {e}")
    print(f"   ✗ beautifulsoup4")

try:
    import fastapi
    print("   ✓ fastapi")
except ImportError as e:
    errors.append(f"fastapi: {e}")
    print(f"   ✗ fastapi")

if errors:
    print("\n❌ Erreurs détectées:")
    for error in errors:
        print(f"   - {error}")
    sys.exit(1)
else:
    print("\n✅ Tous les modules importés avec succès!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ Installation terminée!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo ""
    echo "1. Configurez votre clé API:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Éditez avec votre clé API"
    echo ""
    echo "2. Lancez l'interface de chat:"
    echo "   ./run_chat.sh"
    echo "   ou"
    echo "   source venv/bin/activate && streamlit run chat_ui.py"
    echo ""
    echo "3. Ou lancez l'API:"
    echo "   source venv/bin/activate && python main.py"
    echo ""
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}❌ Installation échouée${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo "Consultez INSTALLATION.md pour le dépannage"
    exit 1
fi
