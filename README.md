# AI Web Reader

Une application IA capable de lire le contenu d'un site web et de répondre à des questions avec des fonctionnalités anti-hallucination.

## Caractéristiques

### Fonctionnalités principales

- **Scraping web intelligent** : Extraction automatique du contenu textuel des sites web
- **Recherche sémantique** : Base de données vectorielle (ChromaDB) pour une recherche efficace
- **Questions-Réponses IA** : Utilise Claude (Anthropic) pour répondre aux questions
- **Mise à jour automatique** : Détection des changements et rafraîchissement automatique du contenu
- **Anti-hallucination** : Protections robustes contre l'invention de contenu

### Protections anti-hallucination

1. **RAG (Retrieval Augmented Generation)** : Toutes les réponses sont basées uniquement sur le contenu récupéré
2. **Citations obligatoires** : Chaque réponse cite ses sources
3. **Vérification des sources** : Affichage des extraits exacts utilisés
4. **Évaluation de confiance** : Indicateur de confiance pour chaque réponse
5. **Réponse "Je ne sais pas"** : Refuse de répondre si l'information n'existe pas
6. **Pas d'ajout d'informations** : Interdiction d'utiliser des connaissances générales

## Installation

### Prérequis

- Python 3.8+
- Clé API Anthropic

### Étapes d'installation

1. Cloner le dépôt :
```bash
git clone <your-repo-url>
cd web_bot
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer l'environnement :
```bash
cp .env.example .env
```

5. Éditer le fichier `.env` avec vos paramètres :
```env
ANTHROPIC_API_KEY=votre_clé_api_ici
TARGET_URL=https://example.com
UPDATE_FREQUENCY=60
```

## Utilisation

### Démarrage de l'application

```bash
python main.py
```

L'API sera disponible sur `http://localhost:8000`

### Documentation API

Une fois l'application démarrée, accédez à :
- Documentation interactive : `http://localhost:8000/docs`
- Documentation alternative : `http://localhost:8000/redoc`

### Endpoints API

#### 1. Poser une question

```bash
POST /ask
```

**Exemple de requête** :
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quel est le sujet principal du site?",
    "n_sources": 5
  }'
```

**Exemple de réponse** :
```json
{
  "answer": "Selon Source 1, le site traite de...",
  "sources": [
    {
      "text": "Extrait du texte source...",
      "url": "https://example.com",
      "title": "Titre de la page",
      "relevance_score": 0.85
    }
  ],
  "confidence": "high",
  "question": "Quel est le sujet principal du site?"
}
```

#### 2. Question avec streaming

```bash
POST /ask/stream
```

**Exemple** :
```bash
curl -X POST "http://localhost:8000/ask/stream" \
  -H "Content-Type: application/json" \
  -d '{"question": "Expliquez le contenu principal"}' \
  --no-buffer
```

#### 3. Vérifier le statut

```bash
GET /status
```

**Exemple de réponse** :
```json
{
  "status": "running",
  "target_url": "https://example.com",
  "last_update": "2024-01-15T10:30:00",
  "update_count": 5,
  "collection_size": 150,
  "update_frequency_minutes": 60
}
```

#### 4. Forcer une mise à jour

```bash
POST /update
```

```bash
curl -X POST "http://localhost:8000/update"
```

#### 5. Health check

```bash
GET /health
```

## Architecture

```
web_bot/
├── config.py           # Gestion de la configuration
├── scraper.py          # Module de scraping web
├── vector_store.py     # Interface ChromaDB
├── qa_engine.py        # Moteur Q&A avec anti-hallucination
├── updater.py          # Système de mise à jour automatique
├── api.py              # API FastAPI
├── main.py             # Point d'entrée
└── requirements.txt    # Dépendances
```

### Flux de données

1. **Scraping** : Le `WebScraper` extrait le contenu du site web
2. **Stockage** : Le contenu est divisé en chunks et stocké dans ChromaDB
3. **Question** : L'utilisateur pose une question via l'API
4. **Recherche** : Le `VectorStore` trouve les chunks pertinents
5. **Génération** : Le `QAEngine` génère une réponse basée uniquement sur les sources
6. **Réponse** : La réponse avec citations et sources est retournée

### Détection des changements

- Hash SHA256 du contenu HTML
- Comparaison automatique à chaque mise à jour
- Rafraîchissement uniquement si le contenu a changé

## Exemples d'utilisation Python

### Exemple de client simple

```python
import requests

API_URL = "http://localhost:8000"

def ask_question(question: str):
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question, "n_sources": 5}
    )
    result = response.json()

    print(f"Question: {result['question']}")
    print(f"Confiance: {result['confidence']}")
    print(f"\nRéponse:\n{result['answer']}\n")

    print("Sources:")
    for i, source in enumerate(result['sources'], 1):
        print(f"\n[Source {i}]")
        print(f"URL: {source['url']}")
        print(f"Extrait: {source['text']}")
        print(f"Score: {source['relevance_score']:.2f}")

# Utilisation
ask_question("Quel est le contenu principal du site?")
```

### Exemple avec streaming

```python
import requests
import json

def ask_with_streaming(question: str):
    response = requests.post(
        f"{API_URL}/ask/stream",
        json={"question": question},
        stream=True
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if data['type'] == 'answer_chunk':
                print(data['content'], end='', flush=True)
            elif data['type'] == 'sources':
                print("\n\nSources utilisées:")
                for source in data['content']:
                    print(f"- {source['title']}: {source['url']}")
                print("\nRéponse: ", end='')

ask_with_streaming("Expliquez le contenu")
```

## Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Anthropic (obligatoire) | - |
| `TARGET_URL` | URL du site web à scraper (obligatoire) | - |
| `UPDATE_FREQUENCY` | Fréquence de mise à jour en minutes | 60 |
| `CHROMA_PERSIST_DIRECTORY` | Répertoire pour ChromaDB | ./chroma_db |
| `API_HOST` | Hôte de l'API | 0.0.0.0 |
| `API_PORT` | Port de l'API | 8000 |

### Personnalisation du scraping

Pour modifier la taille des chunks ou le comportement du scraper, éditez `scraper.py`:

```python
# Modifier la taille des chunks
chunks = self.extract_text_chunks(html, chunk_size=2000)

# Modifier les éléments HTML à extraire
for element in soup.find_all(['p', 'h1', 'h2', 'article']):
    # ...
```

## Sécurité et bonnes pratiques

1. **Ne commitez jamais votre `.env`** : Contient des clés API sensibles
2. **Limitez les requêtes** : Implémentez un rate limiting pour la production
3. **HTTPS en production** : Utilisez toujours HTTPS pour l'API en production
4. **Validez les URLs** : Vérifiez que les URLs scrappées sont autorisées
5. **Monitoring** : Surveillez les logs pour détecter les erreurs

## Résolution des problèmes

### L'application ne démarre pas

- Vérifiez que toutes les dépendances sont installées
- Vérifiez que la clé API Anthropic est valide
- Vérifiez les logs pour les erreurs spécifiques

### Pas de réponses ou réponses vides

- Vérifiez que le site web est accessible
- Vérifiez qu'au moins une mise à jour a été effectuée (`/status`)
- Forcez une mise à jour avec `POST /update`

### Erreurs de scraping

- Certains sites bloquent les scrapers : ajoutez un User-Agent valide
- Vérifiez les permissions et robots.txt du site
- Certains sites nécessitent JavaScript : envisagez d'utiliser Playwright

## Limitations

- Le scraping ne fonctionne que sur les sites statiques ou rendus côté serveur
- Les sites nécessitant JavaScript peuvent nécessiter Playwright
- Le coût de l'API Claude dépend du nombre de requêtes
- La taille du contenu est limitée par ChromaDB et la mémoire

## Améliorations futures

- Support multi-sites
- Cache des réponses fréquentes
- Interface web interactive
- Support de fichiers PDF et documents
- Authentification et autorisation
- Métriques et analytics
- Support multilingue amélioré

## Licence

Voir le fichier LICENSE pour plus de détails.

## Support

Pour des questions ou des problèmes, ouvrez une issue sur GitHub.
