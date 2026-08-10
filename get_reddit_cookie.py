#!/usr/bin/env python3
"""
Helper script to display Reddit Session Token instructions.
"""
import sys

print("""
===================================================================
🔑 COMMENT RECUPERER VOTRE JETON DE SESSION REDDIT EN 5 SECONDES :
===================================================================

Puisque vous etes DEJA connecte a votre compte Reddit dans votre navigateur :

1. Sur votre navigateur (Chrome / Edge / Firefox) avec Reddit ouvert :
   - Appuyez sur la touche F12 (Inspecter l'element).
   - Allez dans l'onglet "Application" (ou "Stockage").
   - Cliquez sur "Cookies" -> "https://www.reddit.com".
   - Trouvez le cookie appele "reddit_session" ou "token".
   - Copiez sa valeur.

2. Sur votre depot GitHub (ai-reddit-bot-taximarnavallee) :
   - Allez dans Settings -> Secrets and variables -> Actions.
   - Ajoutez un nouveau secret nomme : REDDIT_SESSION_TOKEN
   - Collez la valeur du jeton.

===================================================================
✨ C'EST FINI ! Le Bot Cloud postera 100% SEUL 24/7 (ORDI ETEINT).
===================================================================
""")
