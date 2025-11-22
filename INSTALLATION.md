# Guide d'Installation Détaillé

## ⚠️ Migration ChromaDB 0.5.20

**Si vous mettez à jour depuis une version antérieure**, consultez [MIGRATION_0.5.md](MIGRATION_0.5.md) pour les changements importants.

## Problèmes Courants et Solutions

### Erreur: `Could not connect to tenant default_tenant`

**Symptôme:** Erreur lors du lancement du chat ou de l'API: `Could not connect to tenant default_tenant. Are you sure it exists?`

**Cause:** Cette erreur se produit après une mise à jour vers ChromaDB 0.5.20. L'ancienne base de données n'est pas compatible.

**Solution:**
```bash
# Supprimez l'ancien répertoire ChromaDB
rm -rf ./chroma_db

# Redémarrez l'application
./run_chat.sh
```

Le répertoire sera recréé automatiquement avec la nouvelle API.

### Erreur: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Symptôme:** Erreur lors du lancement du chat: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Cause:** Caches obsolètes contenant des références à d'anciennes versions des bibliothèques.

**Solution rapide:**
```bash
# Linux/Mac
./clean_caches.sh

# Windows
clean_caches.bat
```

Puis relancez l'application.

### Erreur: `Failed building wheel for chroma-hnswlib`

**Symptôme:** Erreur de compilation lors de `pip install -r requirements.txt`

**Solution:** Nous avons mis à jour ChromaDB vers la version 0.5.20 qui inclut des wheels pré-compilées pour Python 3.12.

```bash
pip install chromadb==0.5.20
```

### Erreur: SHA256 hash mismatch pour ONNX model

**Symptôme:** `Downloaded file does not match expected SHA256 hash`

**Solution:** C'est un problème temporaire de cache. Deux options:

1. **Nettoyer le cache ChromaDB:**
```bash
rm -rf ~/.cache/chroma/
```

2. **Ignorer (recommandé):** Le modèle se téléchargera correctement lors de la première utilisation réelle.

### Erreur: `SSL: CERTIFICATE_VERIFY_FAILED`

**Symptôme:**
```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate'))
```

**Cause:** Le site web cible utilise un certificat SSL auto-signé ou non reconnu par le système.

**⚠️ Solution (SEULEMENT pour les sites de confiance) :**

Ajoutez cette ligne dans votre fichier `.env` :
```bash
VERIFY_SSL=false
```

**AVERTISSEMENT:** Désactiver la vérification SSL est un risque de sécurité. Ne faites ceci que pour des sites internes ou de confiance absolue.

**Alternative sécurisée:** Installez le certificat racine du site sur votre système ou contactez l'administrateur du site.

### Installation Complète

#### Option 1: Installation Automatique

```bash
# Cloner le projet
git clone https://github.com/votre-repo/web_bot
cd web_bot

# Installer les dépendances
pip install -r requirements.txt

# Si erreur avec ChromaDB, utiliser:
pip install chromadb==0.5.20
pip install -r requirements.txt
```

#### Option 2: Installation Manuelle (si problèmes)

```bash
# Installer ChromaDB d'abord
pip install chromadb==0.5.20

# Installer les autres dépendances principales
pip install beautifulsoup4==4.12.3
pip install requests==2.31.0
pip install anthropic==0.39.0
pip install fastapi==0.109.0
pip install uvicorn==0.27.0
pip install streamlit==1.29.0
pip install pydantic-settings==2.1.0
pip install apscheduler==3.10.4
pip install lxml==5.1.0
```

## Dépendances Système

### Ubuntu/Debian

Les outils de compilation sont généralement déjà installés, mais si nécessaire:

```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev
```

### macOS

```bash
xcode-select --install
```

### Windows

Installer [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Vérification de l'Installation

### Test Simple

```bash
python3 -c "import chromadb; import anthropic; import streamlit; print('✓ Installation réussie!')"
```

### Test Complet

```bash
python3 test_basic.py
```

**Résultat attendu:** 3/4 ou 4/4 tests passés

## Environnement Virtuel (Recommandé)

```bash
# Créer l'environnement
python3 -m venv venv

# Activer (Linux/Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

### 1. Fichier .env

```bash
cp .env.example .env
nano .env  # ou votre éditeur préféré
```

Contenu minimum:

```env
ANTHROPIC_API_KEY=sk-ant-votre_clé_ici
TARGET_URL=https://docs.anthropic.com
```

### 2. Sans fichier .env

L'interface graphique permet de configurer directement:
- Lancer `./run_chat.sh`
- Entrer la clé API dans la barre latérale

## Versions de Python

- **Recommandé:** Python 3.11
- **Minimum:** Python 3.8
- **Testé:** Python 3.9, 3.10, 3.11

## Dépendances Optionnelles

### Pour le développement

```bash
pip install pytest black flake8
```

### Pour Docker

```bash
docker-compose up -d
```

## Résolution de Problèmes Avancés

### Conflits de Dépendances

Si vous rencontrez des conflits avec OpenTelemetry ou d'autres paquets:

```bash
# Forcer la réinstallation
pip install --force-reinstall --no-cache-dir chromadb==0.5.20
```

### Permissions

Sur Linux, évitez d'utiliser `sudo pip`. Utilisez plutôt:

```bash
pip install --user -r requirements.txt
```

Ou un environnement virtuel (recommandé).

### Mémoire Insuffisante

ChromaDB peut nécessiter beaucoup de RAM. Si problèmes:

- Réduire `chunk_size` dans `scraper.py`
- Limiter le nombre de documents indexés

## Support

Si vous rencontrez des problèmes:

1. Vérifiez les [Issues GitHub](https://github.com/votre-repo/web_bot/issues)
2. Consultez le README.md
3. Ouvrez une nouvelle issue avec:
   - Votre version de Python (`python --version`)
   - Votre système d'exploitation
   - Le message d'erreur complet
   - Les étapes pour reproduire

## Checklist d'Installation

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dependencies installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` configuré avec API key
- [ ] Tests de base passés (`python test_basic.py`)
- [ ] Interface de chat fonctionnelle (`./run_chat.sh`)

🎉 Vous êtes prêt!
