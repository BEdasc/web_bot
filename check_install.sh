#!/bin/bash
# Script pour vérifier si l'installation est à jour

echo "🔍 Vérification de votre installation..."
echo ""

# Détecter et utiliser l'environnement virtuel si disponible
if [ -d "venv" ]; then
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "📦 Environnement virtuel détecté, activation..."
        source venv/bin/activate
        echo "✅ Environnement virtuel activé"
        echo ""
    else
        echo "✅ Déjà dans l'environnement virtuel"
        echo ""
    fi
    PYTHON_CMD="python"
else
    echo "⚠️  Aucun environnement virtuel trouvé (venv/)"
    echo "   Utilisation de python3 système"
    echo ""
    PYTHON_CMD="python3"
fi

# Vérifier ChromaDB
if $PYTHON_CMD -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')" 2>/dev/null; then
    CHROMA_VERSION=$($PYTHON_CMD -c "import chromadb; print(chromadb.__version__)")
    if [ "$CHROMA_VERSION" = "0.5.20" ]; then
        echo "✅ ChromaDB 0.5.20 (version correcte)"
    elif [ "$CHROMA_VERSION" = "0.5.3" ]; then
        echo "⚠️  ChromaDB $CHROMA_VERSION (version 0.5.20 recommandée pour Python 3.12)"
        echo "   Exécutez: pip install --only-binary=:all: chromadb==0.5.20"
    else
        echo "⚠️  ChromaDB $CHROMA_VERSION (version 0.5.20 recommandée)"
        echo "   Exécutez: pip install --only-binary=:all: chromadb==0.5.20"
    fi
else
    echo "❌ ChromaDB non installé"
    echo "   Exécutez: ./install.sh"
    exit 1
fi

# Vérifier les autres modules
MISSING=0

for module in "anthropic" "streamlit" "fastapi" "beautifulsoup4:bs4" "requests" "pydantic"; do
    MODULE_NAME=$(echo $module | cut -d: -f1)
    IMPORT_NAME=$(echo $module | cut -d: -f2)
    if [ "$IMPORT_NAME" = "$MODULE_NAME" ]; then
        IMPORT_NAME=$MODULE_NAME
    fi
    
    if $PYTHON_CMD -c "import ${IMPORT_NAME}" 2>/dev/null; then
        echo "✅ $MODULE_NAME"
    else
        echo "❌ $MODULE_NAME manquant"
        MISSING=1
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "🎉 Votre installation est complète!"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Configurez .env avec votre clé API"
    echo "2. Lancez: ./run_chat.sh"
else
    echo "⚠️  Modules manquants détectés"
    echo ""
    echo "Options:"
    echo "1. Installation complète: ./install.sh"
    echo "2. Installer uniquement ce qui manque: pip install -r requirements.txt"
fi
