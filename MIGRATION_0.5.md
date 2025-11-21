# Migration vers ChromaDB 0.5.20

## Changements Importants

Nous avons mis à jour ChromaDB de la version 0.5.3 vers 0.5.20 pour assurer une meilleure compatibilité avec Python 3.12.

### Changements d'API

ChromaDB 0.5.x a introduit des changements importants dans son API :

**Ancienne API (0.4.x - 0.5.3) :**
```python
from chromadb.config import Settings as ChromaSettings
client = chromadb.Client(ChromaSettings(
    persist_directory=persist_directory,
    anonymized_telemetry=False
))
```

**Nouvelle API (0.5.20) :**
```python
client = chromadb.PersistentClient(
    path=persist_directory
)
```

## Erreurs Courantes et Solutions

### Erreur 1: "Could not connect to tenant default_tenant"

**Symptôme:**
```
Erreur d'initialisation: Could not connect to tenant default_tenant. Are you sure it exists?
```

**Cause:** Cette erreur se produit quand on utilise l'ancienne API `chromadb.Client()` avec ChromaDB 0.5.x.

**Solution:** Le code a été mis à jour pour utiliser `chromadb.PersistentClient()`. Si vous rencontrez toujours cette erreur :

1. Récupérez les dernières modifications :
   ```bash
   git pull
   ```

2. Si vous avez un ancien répertoire ChromaDB, supprimez-le :
   ```bash
   rm -rf ./chroma_db
   ```

3. Redémarrez l'application :
   ```bash
   ./run_chat.sh
   # ou
   python main.py
   ```

### Erreur 2: "Downloaded file does not match expected SHA256 hash"

**Symptôme:**
```
Downloaded file /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz does not match expected SHA256 hash
```

**Cause:** Le modèle ONNX en cache est corrompu.

**Solution:** Supprimez le cache et laissez ChromaDB retélécharger :
```bash
rm -rf ~/.cache/chroma/onnx_models
```

Puis relancez l'application. Le modèle sera retéléchargé automatiquement.

## Test de Votre Installation

Vous pouvez vérifier que tout fonctionne correctement avec :

```bash
python3 test_chromadb.py
```

Ce script teste :
- ✅ Initialisation de ChromaDB
- ✅ Création de collections
- ✅ Ajout de documents
- ✅ Recherche sémantique

Si tous les tests passent, vous êtes prêt à utiliser l'application !

## Avantages de ChromaDB 0.5.20

- ✅ **Python 3.12 Support:** Wheels pré-compilés pour Python 3.12
- ✅ **API Simplifiée:** API plus claire et plus facile à utiliser
- ✅ **Meilleure Performance:** Optimisations internes
- ✅ **Moins de Dépendances:** Compilation C++ non requise

## Besoin d'Aide ?

Si vous rencontrez des problèmes après la migration :

1. Consultez le fichier `INSTALLATION.md` pour les problèmes courants
2. Exécutez `python3 test_chromadb.py` pour diagnostiquer
3. Vérifiez que vous utilisez Python 3.12.x : `python3 --version`
4. Assurez-vous d'avoir la dernière version : `git pull`

## Logs de Déboggage

Si vous voyez ces messages, c'est normal et sans impact :

```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
```

Ce sont des avertissements de télémétrie qui n'affectent pas le fonctionnement de l'application.
