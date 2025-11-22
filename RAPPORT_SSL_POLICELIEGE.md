# Rapport Technique - Problème de Certificat SSL sur policeliege.be

**Date:** 22 novembre 2024
**Site concerné:** https://policeliege.be/
**Type de problème:** Vérification du certificat SSL échouée

---

## Résumé Exécutif

Le site **policeliege.be** présente un problème de configuration SSL empêchant la vérification correcte du certificat par les clients HTTPS standards. Cette erreur peut affecter l'intégration avec des applications tierces et potentiellement impacter la confiance des utilisateurs.

---

## Erreur Rencontrée

Lors de tentatives de connexion HTTPS au site, l'erreur suivante est retournée :

```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)'))
```

### Détails Techniques

- **Protocole:** HTTPS (port 443)
- **URL testée:** https://policeliege.be/
- **Client:** Python requests 2.31.0 avec urllib3
- **Système:** Linux (Python 3.12.3)
- **Erreur OpenSSL:** `unable to get local issuer certificate`

---

## Causes Probables

L'erreur "unable to get local issuer certificate" indique typiquement l'un des problèmes suivants :

### 1. **Chaîne de Certificats Incomplète** (Cause la plus probable)

Le serveur n'envoie pas la chaîne de certificats complète. Il manque probablement le(s) certificat(s) intermédiaire(s).

**Explication:**
- Certificat du site : ✅ Présent
- Certificat(s) intermédiaire(s) : ❌ Manquant(s)
- Certificat racine : (dans le trust store du client)

Sans les certificats intermédiaires, les clients ne peuvent pas valider la chaîne de confiance jusqu'à l'autorité de certification racine.

### 2. **Certificat Auto-Signé**

Le certificat pourrait être auto-signé au lieu d'être émis par une autorité de certification (CA) reconnue.

### 3. **Ordre Incorrect des Certificats**

Les certificats sont présents mais dans le mauvais ordre dans la chaîne.

### 4. **Certificat Expiré ou Non Encore Valide**

Le certificat pourrait être expiré ou sa période de validité n'a pas encore commencé.

---

## Impact

### Impact Utilisateur
- ❌ Avertissements de sécurité dans certains navigateurs
- ❌ Impossibilité de connexion pour certains clients stricts (applications, API)
- ⚠️ Perte potentielle de confiance des utilisateurs

### Impact Technique
- ❌ Échec de l'intégration avec des systèmes automatisés
- ❌ Impossibilité d'utiliser le site comme source de données pour des applications
- ❌ Problèmes avec les outils de monitoring et de crawling

---

## Diagnostic Recommandé

### 1. Test avec SSL Labs

Utilisez le service gratuit de Qualys SSL Labs :

```
https://www.ssllabs.com/ssltest/analyze.html?d=policeliege.be
```

Ce test fournira un rapport détaillé sur :
- La validité du certificat
- La chaîne de certificats
- Les protocoles supportés
- Les vulnérabilités potentielles

### 2. Test avec OpenSSL

Depuis un terminal Linux/Mac :

```bash
openssl s_client -connect policeliege.be:443 -showcerts
```

Vérifiez :
- Le nombre de certificats retournés (devrait être 2 ou 3)
- La présence de "Verify return code: 0 (ok)" à la fin

### 3. Test de la Chaîne de Certificats

```bash
openssl s_client -connect policeliege.be:443 -CApath /etc/ssl/certs/ < /dev/null
```

Si la vérification échoue, la chaîne est incomplète.

---

## Solutions Recommandées

### Solution 1 : Installer la Chaîne de Certificats Complète (Recommandée)

**Serveur Apache:**

1. Obtenez le bundle complet de votre CA (certificat + intermédiaires)
2. Configurez dans votre VirtualHost :

```apache
SSLEngine on
SSLCertificateFile /path/to/policeliege.be.crt
SSLCertificateKeyFile /path/to/policeliege.be.key
SSLCertificateChainFile /path/to/intermediate.crt
# OU pour Apache 2.4.8+
SSLCertificateFile /path/to/policeliege.be-fullchain.crt
```

3. Redémarrez Apache :
```bash
sudo systemctl restart apache2
```

**Serveur Nginx:**

1. Créez un fichier fullchain.crt contenant :
   - Votre certificat
   - Le(s) certificat(s) intermédiaire(s) (dans l'ordre)

2. Configurez dans votre bloc server :

```nginx
ssl_certificate /path/to/fullchain.crt;
ssl_certificate_key /path/to/policeliege.be.key;
```

3. Testez la configuration :
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Solution 2 : Obtenir un Nouveau Certificat

Si le certificat actuel est problématique, considérez :

**Option A - Let's Encrypt (Gratuit):**
```bash
sudo certbot --apache -d policeliege.be -d www.policeliege.be
```

**Option B - Certificat Commercial:**
- Digicert
- GlobalSign
- Sectigo
- Autres CA reconnues

---

## Vérification Post-Correction

### 1. Test SSL Labs
La note devrait être A ou A+ après correction.

### 2. Test avec Différents Navigateurs
- Chrome/Edge
- Firefox
- Safari

### 3. Test avec OpenSSL
```bash
openssl s_client -connect policeliege.be:443 -CApath /etc/ssl/certs/
# Devrait afficher: Verify return code: 0 (ok)
```

### 4. Test avec cURL
```bash
curl -v https://policeliege.be/
# Devrait se connecter sans erreur SSL
```

---

## Recommandations Supplémentaires

### Sécurité SSL/TLS

1. **Désactiver les protocoles obsolètes:**
   - Désactiver SSLv2, SSLv3, TLS 1.0, TLS 1.1
   - Utiliser uniquement TLS 1.2 et TLS 1.3

2. **Configurer HSTS (HTTP Strict Transport Security):**
```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

3. **Activer OCSP Stapling:**
```apache
SSLUseStapling on
SSLStaplingCache "shmcb:logs/ssl_stapling(32768)"
```

### Monitoring

Mettez en place une surveillance pour :
- Expiration du certificat (alertes 30j avant)
- Validité de la chaîne de certificats
- Note SSL Labs

---

## Ressources Utiles

- **SSL Labs:** https://www.ssllabs.com/
- **Mozilla SSL Configuration Generator:** https://ssl-config.mozilla.org/
- **Let's Encrypt:** https://letsencrypt.org/
- **OpenSSL Documentation:** https://www.openssl.org/docs/

---

## Contact

Pour toute question concernant ce rapport, n'hésitez pas à nous contacter.

**Note:** Ce problème affecte l'intégrabilité de votre site avec des systèmes tiers. Une résolution rapide est recommandée pour maintenir la confiance des utilisateurs et permettre l'intégration avec des applications externes.
