@echo off
REM Script de nettoyage complet pour résoudre les problèmes de compatibilité

echo Nettoyage des caches et bases de donnees...
echo.

REM 1. Nettoyer le cache ChromaDB
if exist "%USERPROFILE%\.cache\chroma" (
    echo [CLEAN] Suppression du cache ChromaDB...
    rmdir /s /q "%USERPROFILE%\.cache\chroma"
    echo [OK] Cache ChromaDB supprime
)

REM 2. Nettoyer l'ancienne base de données ChromaDB locale
if exist "chroma_db" (
    echo [CLEAN] Suppression de l'ancienne base de donnees ChromaDB...
    rmdir /s /q chroma_db
    echo [OK] Ancienne base ChromaDB supprimee
)

REM 3. Nettoyer le cache Streamlit
if exist "%USERPROFILE%\.streamlit\cache" (
    echo [CLEAN] Suppression du cache Streamlit...
    rmdir /s /q "%USERPROFILE%\.streamlit\cache"
    echo [OK] Cache Streamlit supprime
)

REM 4. Nettoyer les fichiers __pycache__
echo [CLEAN] Suppression des fichiers Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo [OK] Fichiers Python cache supprimes

REM 5. Nettoyer les anciennes sessions Streamlit
if exist "%USERPROFILE%\.streamlit\sessions" (
    rmdir /s /q "%USERPROFILE%\.streamlit\sessions"
    echo [OK] Sessions Streamlit supprimees
)

echo.
echo [OK] Nettoyage termine!
echo.
echo Prochaines etapes:
echo 1. Mettez a jour les dependances: pip install -r requirements.txt --upgrade
echo 2. Lancez l'application: run_chat.bat
echo.
pause
