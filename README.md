# Observatoire des taux

**Ce que coûte l'argent en zone euro, et ce que ça change : pour une salle de marchés comme pour un épargnant.**

**En ligne : [observatoire-taux.vercel.app](https://observatoire-taux.vercel.app)** · données officielles mises à jour chaque soir de semaine.

## Ce que montre la page

| | Ce qu'on y voit | Pourquoi c'est utile |
|---|---|---|
| L'essentiel | OAT 10 ans, écart avec l'Allemagne, taux de la BCE, inflation, Livret A, et cinq constats calculés | La situation en 10 secondes |
| **Côté marchés** | | |
| Écart à 10 ans avec l'Allemagne | France, Italie, Espagne depuis 1993, avec les événements qui l'ont fait bouger | Mesure la confiance des marchés dans un pays |
| Courbe des taux | Taux des États AAA de 3 mois à 30 ans : aujourd'hui, il y a 1 an, il y a 3 ans | La forme de la courbe résume les anticipations |
| Pente 10 ans − 2 ans | Depuis 2004 ; inversée en 2022-2024 | Signal suivi de près par les desks de taux |
| Position sur l'écart France-Allemagne | Acheter l'OAT, vendre le Bund, entre deux dates : résultat, DV01, pire et meilleur moment | Comment un trader exprime une vue sur la France |
| Risque d'une obligation | Prix, duration, convexité, DV01, effet d'un mouvement de taux | La mesure de risque de base d'un desk |
| **Côté épargnants** | | |
| Taux réels | OAT 10 ans et Livret A, inflation déduite, depuis 2008 | Ce que rapporte vraiment l'épargne |
| Fonds euros et taux | Rendement des fonds euros face aux taux et à l'inflation | Pourquoi le fonds euros suit les taux avec retard |
| Pour un client | Perte d'une obligation si les taux montent, pouvoir d'achat du Livret A | Une réponse prête pour un rendez-vous |

## Données : uniquement des sources officielles et réutilisables

| Donnée | Source | Fréquence |
|---|---|---|
| Courbe des taux des États de la zone euro notés AAA, taux de dépôt | Banque centrale européenne (data.ecb.europa.eu) | quotidienne |
| Taux à 10 ans par pays (FR, DE, IT, ES) | Eurostat, `irt_lt_mcby_m` (critère de convergence) | mensuelle, depuis 1993 |
| Inflation (indice des prix harmonisé) | Eurostat, `prc_hicp_minr` | mensuelle |
| Livret A, fonds euros, événements | Écrits à la main avec leur source dans [`observatoire/reperes.py`](observatoire/reperes.py) | à chaque changement |

Les indices TEC de la Banque de France ne sont pas utilisés : leurs conditions interdisent la redistribution.

## Comment ça marche

```
GitHub Actions, chaque soir ──> observatoire/mettre_a_jour.py ──> data/donnees.json ──> la page le lit
                                 (BCE + Eurostat)                    (tests avant publication)
```

- [`obligations.py`](observatoire/obligations.py) : prix d'une obligation (flux actualisés), duration modifiée, convexité, DV01.
- [`analyses.py`](observatoire/analyses.py) : écarts, taux réels, position sur l'écart, et les constats du jour (aucune phrase écrite à la main : chaque chiffre vient d'un calcul).
- La page exécute **ce même code Python** dans le navigateur (Pyodide).
- [Tests](tests/test_calculs.py) sur des cas calculés à la main : une obligation dont le coupon égale le taux vaut 100 ; un zéro-coupon à 10 ans à 5 % vaut 100 / 1,05¹⁰ ; une hausse de 1 point fait perdre 8,1 % à une OAT 10 ans à 3 %, etc.

## Lancer

```bash
pip install certifi pytest
python -m observatoire.mettre_a_jour     # télécharge les données
python -m pytest tests                   # vérifie les calculs
python -m http.server                    # puis ouvrir http://localhost:8000
```

## Limites

- Courbe des taux : celle des États notés AAA (calculée par la BCE), pas une courbe propre à la France, faute de données françaises quotidiennes réutilisables.
- Écarts par pays en moyenne mensuelle.
- Position sur l'écart : approximation pédagogique (sans portage ni coût de financement).

---

Projet personnel de Gabin Eby Klein, conçu et piloté avec Claude.
**Document pédagogique : ne constitue ni un conseil en investissement ni une recommandation.**
