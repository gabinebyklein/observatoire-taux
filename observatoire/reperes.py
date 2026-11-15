"""Repères qui ne viennent pas d'une API : écrits à la main, chacun avec sa source."""

# Taux du Livret A (date d'effet, taux en %). Fixé par arrêté, publié par la Banque de France et service-public.fr.
# Derniers changements vérifiés le 15/11/2026 : https://www.service-public.gouv.fr/particuliers/actualites/A15818
LIVRET_A = [
    ("2008-08-01", 4.00), ("2009-02-01", 2.50), ("2009-05-01", 1.75), ("2009-08-01", 1.25), ("2010-08-01", 1.75),
    ("2011-02-01", 2.00), ("2011-08-01", 2.25), ("2013-02-01", 1.75), ("2013-08-01", 1.25), ("2014-08-01", 1.00),
    ("2015-08-01", 0.75), ("2020-02-01", 0.50), ("2022-02-01", 1.00), ("2022-08-01", 2.00), ("2023-02-01", 3.00),
    ("2025-02-01", 2.40), ("2025-08-01", 1.70), ("2026-02-01", 1.50), ("2026-08-01", 1.70),
]

# Taux moyen de revalorisation des fonds euros (contrats individuels), avant prélèvements sociaux.
# Source : rapports annuels de l'ACPR (Banque de France), repris par la presse spécialisée (mars et juillet 2026).
FONDS_EUROS = [("2022", 1.91), ("2023", 2.60), ("2024", 2.63), ("2025", 2.63)]

# Événements qui ont fait bouger l'écart France-Allemagne (mois, libellé court)
EVENEMENTS = [
    ("2011-11", "Crise des dettes de la zone euro"),
    ("2012-07", "« Whatever it takes » (Draghi)"),
    ("2015-03", "La BCE lance ses rachats de dette"),
    ("2017-04", "Présidentielle française"),
    ("2020-03", "Covid : programme d'urgence de la BCE"),
    ("2022-07", "Première hausse de taux de la BCE depuis 2011"),
    ("2024-06", "Dissolution de l'Assemblée nationale"),
    ("2024-12", "Censure du gouvernement Barnier"),
    ("2025-09", "Chute du gouvernement Bayrou"),
]
