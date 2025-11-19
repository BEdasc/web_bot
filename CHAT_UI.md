# Interface de Chat Graphique 🤖

Interface graphique moderne pour interagir avec l'AI Web Reader via une application de chat.

## Aperçu

L'interface de chat offre une expérience utilisateur conviviale pour poser des questions sur le contenu de sites web indexés. Elle affiche les réponses avec des citations de sources, des indicateurs de confiance, et permet de gérer facilement le système.

## Fonctionnalités

### Interface de Chat
- 💬 **Conversation fluide** : Interface de chat moderne et intuitive
- 🎨 **Design épuré** : Messages utilisateur et assistant clairement distingués
- ⏱️ **Horodatage** : Timestamp pour chaque message
- 📜 **Historique** : Conservation de l'historique de conversation

### Affichage des Réponses
- 🎯 **Indicateur de confiance** : Badge coloré (Haute/Moyenne/Faible)
- 📚 **Sources expandables** : Voir les sources utilisées en un clic
- 🔗 **Liens cliquables** : Accès direct aux URLs sources
- 📊 **Score de pertinence** : Pourcentage de pertinence pour chaque source

### Configuration
- ⚙️ **Configuration en ligne** : API key et URL cible modifiables
- 🔄 **Mise à jour manuelle** : Bouton pour rafraîchir le contenu
- 🗑️ **Effacement du chat** : Nettoyer l'historique rapidement
- 👁️ **Toggle sources** : Afficher/masquer les sources

### Statut Système
- 📊 **Métriques en temps réel** : Nombre de documents indexés
- 🟢 **Indicateur d'état** : En ligne/Hors ligne
- ℹ️ **Informations** : URL cible actuelle

## Installation et Démarrage

### Méthode 1 : Script de lancement automatique (Recommandé)

**Linux/Mac :**
```bash
./run_chat.sh
```

**Windows :**
```bash
run_chat.bat
```

Le script va automatiquement :
1. Créer l'environnement virtuel si nécessaire
2. Installer les dépendances
3. Lancer l'application
4. Ouvrir votre navigateur

### Méthode 2 : Lancement manuel

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Installer les dépendances (si pas déjà fait)
pip install -r requirements.txt

# Lancer l'application
streamlit run chat_ui.py
```

L'application sera accessible sur : **http://localhost:8501**

## Configuration

### Option A : Fichier .env (recommandé)

Créez un fichier `.env` avec :

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
TARGET_URL=https://docs.anthropic.com
UPDATE_FREQUENCY=60
```

### Option B : Interface graphique

Si vous n'avez pas de fichier `.env`, vous pouvez configurer directement dans la barre latérale :

1. Entrez votre clé API Anthropic
2. Configurez l'URL cible
3. Cliquez sur "Mettre à jour" pour indexer le contenu

## Utilisation

### Première utilisation

1. **Configurer l'API Key**
   - Dans la barre latérale, entrez votre clé API Anthropic
   - Ou créez un fichier `.env` avec `ANTHROPIC_API_KEY`

2. **Configurer l'URL cible**
   - Entrez l'URL du site web à analyser
   - Exemple : `https://docs.anthropic.com`

3. **Indexer le contenu**
   - Cliquez sur "🔄 Mettre à jour" dans la barre latérale
   - Attendez que l'indexation se termine
   - Le statut affichera le nombre de documents indexés

4. **Poser des questions**
   - Tapez votre question dans le champ de chat
   - Appuyez sur Entrée ou cliquez sur l'icône d'envoi
   - La réponse apparaîtra avec les sources

### Fonctionnalités principales

#### Poser une question

```
👤 Vous : "Quel est le sujet principal du site?"

🤖 Assistant : [Confiance: HAUTE]
"Selon Source 1, le site traite de la documentation Claude API..."
```

#### Voir les sources

Cliquez sur l'expandeur "📚 Sources" pour voir :
- Titre du document source
- URL complète (cliquable)
- Score de pertinence
- Extrait de texte utilisé

#### Mettre à jour le contenu

1. Cliquez sur "🔄 Mettre à jour"
2. Le système vérifie si le contenu a changé
3. Si changements détectés : réindexation automatique
4. Si aucun changement : message informatif

#### Effacer l'historique

Cliquez sur "🗑️ Effacer chat" pour nettoyer la conversation.

## Indicateurs de Confiance

Les réponses incluent un indicateur de confiance :

- 🟢 **HAUTE** : Plusieurs sources pertinentes trouvées
- 🟠 **MOYENNE** : Quelques sources, pertinence modérée
- 🔴 **FAIBLE** : Peu de sources ou pertinence faible
- ⚫ **AUCUNE** : Impossible de répondre avec les données disponibles

## Personnalisation

### Thème et couleurs

Éditez `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#2196F3"      # Bleu principal
backgroundColor = "#FFFFFF"    # Fond blanc
secondaryBackgroundColor = "#F5F5F5"  # Fond secondaire gris clair
textColor = "#262730"         # Texte foncé
```

### CSS personnalisé

Le fichier `chat_ui.py` contient des styles CSS personnalisables dans la fonction `load_css()`.

## Résolution de problèmes

### Erreur : "Module 'streamlit' not found"

```bash
pip install streamlit
```

### Erreur : "Invalid API key"

1. Vérifiez votre clé API dans la barre latérale
2. Ou vérifiez le fichier `.env`
3. Assurez-vous que la clé commence par `sk-ant-`

### Aucune donnée indexée

1. Vérifiez que l'URL est accessible
2. Cliquez sur "Mettre à jour"
3. Attendez la fin de l'indexation
4. Vérifiez les logs dans le terminal

### L'application ne s'ouvre pas

1. Vérifiez que le port 8501 est disponible
2. Essayez : `streamlit run chat_ui.py --server.port 8502`
3. Vérifiez les erreurs dans le terminal

### Réponses vides ou incohérentes

1. Vérifiez que le site web est bien indexé
2. Forcez une mise à jour du contenu
3. Vérifiez que votre question est claire et liée au contenu

## Avantages de l'Interface Graphique

### vs. CLI

- ✅ Interface visuelle intuitive
- ✅ Historique de conversation visible
- ✅ Sources expandables
- ✅ Configuration en temps réel
- ✅ Pas de commandes à mémoriser

### vs. API

- ✅ Pas besoin de code
- ✅ Feedback visuel immédiat
- ✅ Gestion facile de l'état
- ✅ Idéal pour l'exploration interactive

## Cas d'usage

### Recherche et exploration

Idéal pour explorer le contenu d'un site web de documentation :

```
Q: Quelles sont les fonctionnalités principales?
Q: Comment fonctionne l'authentification?
Q: Y a-t-il des exemples de code?
```

### Support client

Utilisez pour créer un assistant de support basé sur votre documentation :

```
Q: Comment réinitialiser mon mot de passe?
Q: Quels sont les tarifs?
Q: Comment contacter le support?
```

### Veille technologique

Surveillez les changements sur un site concurrent ou une source d'actualités :

```
1. Configurez l'URL cible
2. Activez les mises à jour automatiques
3. Posez des questions régulièrement
```

## Performance

### Optimisations

- **Cache Streamlit** : Les composants système sont mis en cache
- **ChromaDB** : Recherche vectorielle ultra-rapide
- **Chunking intelligent** : Découpage optimal du contenu

### Limitations

- **Taille du contenu** : Limité par la mémoire disponible
- **Taux API** : Limité par votre quota Anthropic
- **Sites dynamiques** : JavaScript non supporté (utiliser Playwright)

## Sécurité

### Bonnes pratiques

1. **Ne partagez jamais votre clé API**
2. **Utilisez HTTPS en production**
3. **Limitez l'accès à l'interface**
4. **Validez les URLs cibles**
5. **Surveillez l'utilisation de l'API**

### Données sensibles

L'application ne stocke pas :
- Vos clés API (en session seulement)
- Vos conversations (en mémoire seulement)
- Données personnelles

## Déploiement

### Streamlit Cloud

```bash
# Commitez votre code
git add .
git commit -m "Add chat UI"
git push

# Sur Streamlit Cloud :
1. Connectez votre repo GitHub
2. Sélectionnez chat_ui.py
3. Ajoutez vos secrets (API key)
4. Déployez !
```

### Docker

Ajoutez au `docker-compose.yml` :

```yaml
chat-ui:
  build: .
  command: streamlit run chat_ui.py --server.port 8501
  ports:
    - "8501:8501"
  env_file:
    - .env
```

## Raccourcis clavier

- `Ctrl + L` : Focus sur le champ de saisie
- `Enter` : Envoyer le message
- `Ctrl + R` : Recharger l'application
- `Ctrl + C` : Arrêter l'application (dans le terminal)

## FAQ

**Q: Puis-je utiliser plusieurs sites web ?**
R: Actuellement, un seul site à la fois. Changez l'URL et mettez à jour pour indexer un nouveau site.

**Q: Les conversations sont-elles sauvegardées ?**
R: Non, elles sont perdues au rechargement. Utilisez le bouton "Copier" du navigateur si nécessaire.

**Q: Combien coûte l'utilisation ?**
R: Seuls les appels à l'API Claude sont facturés par Anthropic. ChromaDB et Streamlit sont gratuits.

**Q: Puis-je personnaliser l'interface ?**
R: Oui ! Éditez `chat_ui.py` pour modifier l'apparence et le comportement.

## Support

- 📖 Voir README.md pour la documentation générale
- 🐛 Rapporter un bug sur GitHub Issues
- 💡 Suggestions : Ouvrir une discussion GitHub

---

**Profitez de votre interface de chat ! 🚀**
