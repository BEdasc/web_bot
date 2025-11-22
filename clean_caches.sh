#!/bin/bash

# Script de nettoyage complet pour résoudre les problèmes de compatibilité

echo "🧹 Nettoyage des caches et bases de données..."

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Nettoyer le cache ChromaDB
if [ -d "$HOME/.cache/chroma" ]; then
    echo -e "${YELLOW}Suppression du cache ChromaDB...${NC}"
    rm -rf "$HOME/.cache/chroma"
    echo -e "${GREEN}✅ Cache ChromaDB supprimé${NC}"
fi

# 2. Nettoyer l'ancienne base de données ChromaDB locale
if [ -d "./chroma_db" ]; then
    echo -e "${YELLOW}Suppression de l'ancienne base de données ChromaDB...${NC}"
    rm -rf ./chroma_db
    echo -e "${GREEN}✅ Ancienne base ChromaDB supprimée${NC}"
fi

# 3. Nettoyer le cache Streamlit
if [ -d "$HOME/.streamlit" ]; then
    echo -e "${YELLOW}Suppression du cache Streamlit...${NC}"
    rm -rf "$HOME/.streamlit/cache"
    echo -e "${GREEN}✅ Cache Streamlit supprimé${NC}"
fi

# 4. Nettoyer les fichiers __pycache__
echo -e "${YELLOW}Suppression des fichiers Python cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo -e "${GREEN}✅ Fichiers Python cache supprimés${NC}"

# 5. Nettoyer les anciennes sessions Streamlit
if [ -d "$HOME/.streamlit/sessions" ]; then
    rm -rf "$HOME/.streamlit/sessions"
    echo -e "${GREEN}✅ Sessions Streamlit supprimées${NC}"
fi

echo ""
echo -e "${GREEN}✅ Nettoyage terminé!${NC}"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Mettez à jour les dépendances: pip install -r requirements.txt --upgrade"
echo "2. Lancez l'application: ./run_chat.sh"
echo ""
