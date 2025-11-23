# Guide du Web Crawler

## Vue d'Ensemble

L'AI Web Reader intègre maintenant un **crawler web intelligent** capable de parcourir automatiquement tout un site web au lieu d'une seule page.

## Modes de Scraping

### Mode Single (par défaut)
- Scrape **uniquement** la page à l'URL spécifiée
- Rapide et prévisible
- Idéal pour pages uniques ou documentation simple

### Mode Full (nouveau)
- Parcourt **récursivement** toutes les pages du site
- Suit les liens internes automatiquement
- Idéal pour sites complets, documentation multi-pages, sites d'information

## Configuration

Ajoutez ces lignes dans votre fichier `.env` :

```env
# Active le mode crawler complet
CRAWL_MODE=full

# Nombre maximum de pages à crawler (sécurité)
MAX_PAGES=100

# Profondeur maximale de liens (0 = page de départ uniquement)
MAX_DEPTH=3

# Délai entre requêtes en secondes (politesse envers le serveur)
CRAWL_DELAY=1.0

# Ne crawler que les liens du même domaine
SAME_DOMAIN_ONLY=true

# Patterns à exclure (séparés par virgules)
EXCLUDE_PATTERNS=.pdf,.jpg,.png,.gif,/admin,/login
```

## Exemples de Configuration

### Exemple 1 : Site de Documentation Complet

```env
TARGET_URL=https://docs.example.com
CRAWL_MODE=full
MAX_PAGES=200
MAX_DEPTH=4
CRAWL_DELAY=1.0
SAME_DOMAIN_ONLY=true
EXCLUDE_PATTERNS=.pdf,/api-reference
```

**Résultat :** Crawle jusqu'à 200 pages de documentation, jusqu'à 4 niveaux de profondeur, en excluant les PDFs.

### Exemple 2 : Site Institutionnel (comme policeliege.be)

```env
TARGET_URL=https://policeliege.be/
CRAWL_MODE=full
MAX_PAGES=50
MAX_DEPTH=2
CRAWL_DELAY=2.0
SAME_DOMAIN_ONLY=true
EXCLUDE_PATTERNS=.pdf,.doc,.docx,/admin,/login
```

**Résultat :** Crawle jusqu'à 50 pages, 2 niveaux de profondeur, avec un délai de 2 secondes (respectueux).

### Exemple 3 : Page Unique (mode classique)

```env
TARGET_URL=https://example.com/specific-page
CRAWL_MODE=single
```

**Résultat :** Scrape uniquement la page spécifiée (comportement original).

## Paramètres Détaillés

### CRAWL_MODE
- **Valeurs :** `single` ou `full`
- **Défaut :** `single`
- **Description :** Détermine si une seule page ou tout le site est crawlé

### MAX_PAGES
- **Valeurs :** Entier positif (1-1000)
- **Défaut :** 100
- **Description :** Nombre maximum de pages à crawler (limite de sécurité)
- **Recommandation :**
  - Petits sites : 50-100
  - Sites moyens : 100-300
  - Grands sites : 300-1000

### MAX_DEPTH
- **Valeurs :** Entier positif (0-10)
- **Défaut :** 3
- **Description :** Profondeur maximale de liens à suivre depuis la page de départ
- **Exemples :**
  - `0` : Page de départ uniquement
  - `1` : Page de départ + liens directs
  - `2` : + liens des pages liées
  - `3` : + encore un niveau (recommandé)

### CRAWL_DELAY
- **Valeurs :** Nombre décimal (0.5-10.0)
- **Défaut :** 1.0
- **Description :** Délai en secondes entre chaque requête
- **Recommandation :**
  - Sites rapides/CDN : 0.5-1.0
  - Sites normaux : 1.0-2.0
  - Sites lents/publics : 2.0-5.0

### SAME_DOMAIN_ONLY
- **Valeurs :** `true` ou `false`
- **Défaut :** `true`
- **Description :** Ne suivre que les liens du même domaine
- **Recommandation :** Toujours `true` sauf besoins spécifiques

### EXCLUDE_PATTERNS
- **Format :** Liste séparée par virgules
- **Défaut :** `.pdf,.jpg,.png,.gif,/admin,/login`
- **Description :** Patterns d'URLs à exclure du crawling
- **Exemples :**
  - Extensions : `.pdf`, `.doc`, `.zip`
  - Chemins : `/admin`, `/login`, `/private`
  - Sous-domaines : `cdn.`, `media.`

## Fonctionnement du Crawler

1. **Démarrage** : Le crawler commence à l'URL de départ (TARGET_URL)

2. **Extraction de liens** : Sur chaque page, le crawler extrait tous les liens `<a href="...">`

3. **Filtrage** : Les liens sont filtrés selon :
   - Domaine (si SAME_DOMAIN_ONLY=true)
   - Patterns d'exclusion
   - Extensions de fichiers binaires
   - Profondeur maximale

4. **File d'attente** : Les liens valides sont ajoutés à une file d'attente (BFS)

5. **Crawling** : Chaque page est visitée, avec un délai de politesse entre requêtes

6. **Extraction** : Le contenu textuel est extrait et découpé en chunks

7. **Indexation** : Tous les chunks sont indexés dans ChromaDB

## Logs et Monitoring

Le crawler produit des logs détaillés :

```
INFO:WebScraper initialized in 'full' mode for https://example.com
INFO:WebCrawler initialized for https://example.com
INFO:Settings: max_pages=100, max_depth=3, same_domain=True
INFO:Starting crawl from https://example.com
INFO:Crawled [1/100]: https://example.com (depth 0)
INFO:Crawled [2/100]: https://example.com/about (depth 1)
INFO:Crawled [3/100]: https://example.com/services (depth 1)
...
INFO:Full site scrape complete: 45 pages, 312 chunks
INFO:Crawler stats: {'pages_crawled': 45, 'urls_visited': 67, 'max_pages': 100, 'max_depth': 3}
```

## Performance et Bonnes Pratiques

### Optimisation des Performances

1. **Ajustez MAX_PAGES** : Commencez petit (50), augmentez si nécessaire
2. **Limitez MAX_DEPTH** : Profondeur 2-3 suffit généralement
3. **Utilisez EXCLUDE_PATTERNS** : Évitez les sections inutiles
4. **CRAWL_DELAY adapté** : Plus court = plus rapide, mais plus agressif

### Bonnes Pratiques

1. **Respectez les serveurs** : Utilisez un délai raisonnable (≥1.0s)
2. **Testez d'abord** : Commencez avec MAX_PAGES=10 pour tester
3. **Excluez judicieusement** : Médias, admin, auth, API
4. **Surveillez les logs** : Vérifiez que les bonnes pages sont crawlées

### Temps de Crawling Estimé

Avec CRAWL_DELAY=1.0 :
- 50 pages : ~1 minute
- 100 pages : ~2 minutes
- 200 pages : ~4 minutes
- 500 pages : ~10 minutes

## Exemples d'Usage

### Via le Chat UI

1. Éditez `.env` avec les paramètres de crawl
2. Lancez `./run_chat.sh`
3. Cliquez sur "🔄 Mettre à jour" dans la sidebar
4. Le crawler parcourt le site et affiche la progression

### Via l'API

```bash
# Configurez .env avec CRAWL_MODE=full
curl -X POST http://localhost:8000/update
```

### Via CLI

```bash
# Configurez .env avec CRAWL_MODE=full
python cli.py update
```

## Dépannage

### Problème : Trop peu de pages crawlées

**Causes possibles :**
- MAX_DEPTH trop faible → Augmentez à 3-4
- EXCLUDE_PATTERNS trop restrictifs → Révisez les patterns
- Site avec peu de liens internes → Normal

### Problème : Crawler trop lent

**Solutions :**
- Réduisez CRAWL_DELAY (mais restez poli)
- Réduisez MAX_PAGES
- Réduisez MAX_DEPTH

### Problème : Pages indésirables crawlées

**Solutions :**
- Ajoutez patterns à EXCLUDE_PATTERNS
- Vérifiez SAME_DOMAIN_ONLY=true
- Réduisez MAX_DEPTH

### Problème : Erreurs SSL

**Solution :**
```env
VERIFY_SSL=false  # Uniquement pour sites de confiance !
```

## Statistiques de Crawling

Après chaque crawl, les statistiques sont affichées :

```
Crawler stats: {
  'pages_crawled': 45,      # Pages effectivement crawlées
  'urls_visited': 67,       # URLs totales visitées (inclut échecs)
  'max_pages': 100,         # Limite configurée
  'max_depth': 3            # Profondeur max configurée
}
```

## Comparaison Mode Single vs Full

| Critère | Mode Single | Mode Full |
|---------|-------------|-----------|
| Pages | 1 seule | Plusieurs (jusqu'à MAX_PAGES) |
| Temps | Quelques secondes | Quelques minutes |
| Contenu | Limité à une page | Tout le site |
| Complexité | Très simple | Configuration requise |
| Usage | Pages uniques | Documentation, sites complets |
| Chunks typiques | 4-20 | 100-1000+ |

## FAQ

**Q: Puis-je crawler un site externe (pas le mien) ?**
R: Oui, mais respectez le délai (CRAWL_DELAY ≥ 1.0) et vérifiez le robots.txt du site.

**Q: Le crawler respecte-t-il robots.txt ?**
R: Pas automatiquement dans la version actuelle. Ajoutez les chemins interdits dans EXCLUDE_PATTERNS.

**Q: Puis-je crawler plusieurs sites différents ?**
R: Non, un seul site par configuration. Changez TARGET_URL dans .env pour changer de site.

**Q: Le contenu est-il mis à jour automatiquement ?**
R: Oui, selon UPDATE_FREQUENCY. Le crawler re-crawle périodiquement.

**Q: Combien de chunks puis-je avoir au maximum ?**
R: Illimité, mais ChromaDB fonctionne mieux avec <100,000 chunks. Pour de très grands sites, augmentez la taille des chunks.

## Support

Pour plus d'aide :
- Consultez les logs détaillés
- Vérifiez INSTALLATION.md pour les problèmes courants
- Testez avec CRAWL_MODE=single d'abord
- Contactez le support avec les logs complets
