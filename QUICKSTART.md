# Guide de démarrage rapide

## Installation en 5 minutes

### 1. Cloner et installer

```bash
git clone <your-repo>
cd web_bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Créez un fichier `.env`:

```bash
cp .env.example .env
```

Éditez `.env` avec vos paramètres:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
TARGET_URL=https://docs.anthropic.com
UPDATE_FREQUENCY=60
```

### 3. Premiers pas

#### Option A: API (recommandé pour la production)

Démarrez le serveur:

```bash
python main.py
```

Dans un autre terminal, testez:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "De quoi parle ce site?"}'
```

#### Option B: CLI (recommandé pour les tests)

Mode interactif:

```bash
python cli.py interactive
```

Question unique:

```bash
python cli.py ask "Quel est le contenu principal?"
```

#### Option C: Client Python

```bash
python example_client.py
```

### 4. Utilisation avec Docker

```bash
docker-compose up -d
```

## Exemples de questions

Une fois le système démarré, essayez ces questions:

```python
import requests

API = "http://localhost:8000"

# Question basique
response = requests.post(f"{API}/ask", json={
    "question": "Quel est le sujet principal de ce site?"
})
print(response.json()['answer'])

# Vérifier le statut
status = requests.get(f"{API}/status")
print(status.json())

# Forcer une mise à jour
requests.post(f"{API}/update")
```

## Commandes utiles

### Vérifier le statut

```bash
curl http://localhost:8000/status
```

### Forcer une mise à jour

```bash
curl -X POST http://localhost:8000/update
```

### Documentation API interactive

Ouvrez dans votre navigateur:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Résolution de problèmes

### Erreur: "Module not found"

```bash
pip install -r requirements.txt
```

### Erreur: "Invalid API key"

Vérifiez votre clé API Anthropic dans `.env`

### Pas de résultats

Attendez quelques secondes pour la première indexation, ou forcez une mise à jour:

```bash
python cli.py update
```

## Prochaines étapes

1. Lisez le [README.md](README.md) complet pour plus de détails
2. Explorez les exemples dans `example_client.py`
3. Personnalisez le scraping dans `scraper.py`
4. Ajustez les paramètres anti-hallucination dans `qa_engine.py`

## Support

Pour plus d'aide, consultez:
- README.md pour la documentation complète
- Issues GitHub pour les problèmes connus
- Les logs de l'application pour le débogage
