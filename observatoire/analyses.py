"""Analyses calculées sur les données officielles. Aucune phrase n'est écrite à la main : chaque constat vient d'un calcul."""
from .obligations import dv01

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def nb(x, d=2, signe=False):
    """4.891 -> '4,89' ; avec signe : '+1,1' / '−2,1'."""
    t = f"{abs(x):.{d}f}".replace(".", ",")
    return (("+" if x >= 0 else "−") if signe else ("−" if x < 0 else "")) + t


def mois_fr(m):
    """'2026-10' -> 'octobre 2026'."""
    return f"{MOIS[int(m[5:7]) - 1]} {m[:4]}"


def date_fr(d):
    """'2026-09-16' -> '16/09/2026'."""
    return f"{d[8:10]}/{d[5:7]}/{d[:4]}"


def aligner(a, b):
    """Deux séries [(date, valeur)] -> [(date, va, vb)] sur les dates communes."""
    db = dict(b)
    return [(d, va, db[d]) for d, va in a if d in db]


def ecart(a, b):
    """Écart en points entre deux séries de taux (a − b)."""
    return [(d, round(va - vb, 4)) for d, va, vb in aligner(a, b)]


def plus_haut_depuis(serie):
    """Date de la dernière fois où la série était au moins aussi haute qu'aujourd'hui (None si jamais)."""
    d0, v0 = serie[-1]
    avant = [d for d, v in serie[:-1] if v >= v0]
    return avant[-1] if avant else None


def taux_en_vigueur(changements, date):
    """Pour un taux qui change par paliers (Livret A, taux BCE) : sa valeur à une date."""
    valeur = None
    for d, v in changements:
        if d[:len(date)] <= date:
            valeur = v
    return valeur


def taux_reels(taux, inflation):
    """Taux moins inflation sur un an, mois par mois : ce que rapporte vraiment un placement."""
    return [(d, round(t - i, 4)) for d, t, i in aligner(taux, inflation)]


def rejouer_ecart(fr, de, debut, fin, nominal=10_000_000, maturite=10):
    """Rejoue une position sur l'écart France-Allemagne : acheter l'OAT 10 ans, vendre le Bund 10 ans
    (montants calculés pour que la position ne gagne ou ne perde rien si tous les taux bougent ensemble).
    Elle gagne si l'écart se resserre, perd s'il s'élargit : gain ≈ − DV01 × variation de l'écart en points de base.
    Approximation pédagogique : taux moyens mensuels, sans portage ni coûts de financement."""
    serie = [x for x in ecart(fr, de) if debut <= x[0] <= fin]
    if len(serie) < 2:
        return None
    taux_entree = dict(fr)[serie[0][0]]
    sensibilite = dv01(nominal, taux_entree, maturite, taux_entree)        # obligation émise au pair à l'entrée
    chemin = [(d, -(e - serie[0][1]) * 100 * sensibilite) for d, e in serie]
    return {"debut": serie[0][0], "fin": serie[-1][0], "ecart_entree": serie[0][1], "ecart_sortie": serie[-1][1],
            "variation_pb": (serie[-1][1] - serie[0][1]) * 100, "dv01": sensibilite, "nominal": nominal,
            "resultat": chemin[-1][1], "chemin": chemin,
            "pire": min(chemin, key=lambda x: x[1]), "meilleur": max(chemin, key=lambda x: x[1])}


def lecture(d):
    """Les constats du jour, tous calculés à partir des données."""
    fr, de, it = d["dix_ans"]["FR"], d["dix_ans"]["DE"], d["dix_ans"]["IT"]
    mois = fr[-1][0]
    ecart_de = ecart(fr, de)
    ecart_it = ecart(fr, it)
    c = d["courbe"]["taux"]["aujourd_hui"]
    pente = d["pente_2_10"][-1][1]
    infl = d["inflation"]["FR"][-1]
    livret = taux_en_vigueur(d["livret_a"], d["courbe"]["dates"]["aujourd_hui"])
    bce = d["taux_depot_bce"][-1]
    constats = []
    depuis = plus_haut_depuis(ecart_de)
    constats.append({"theme": "ecart", "texte":
        f"En {mois_fr(mois)}, la France emprunte à 10 ans à {nb(fr[-1][1])} %, contre {nb(de[-1][1])} % pour l'Allemagne : "
        f"un écart de {nb(ecart_de[-1][1])} point, "
        + (f"le plus élevé depuis {mois_fr(depuis)}." if depuis else "le plus élevé de toute la série.")})
    constats.append({"theme": "italie", "texte":
        f"L'Italie emprunte à {nb(it[-1][1])} % : la France paie "
        + (f"{nb(ecart_it[-1][1])} point de plus qu'elle." if ecart_it[-1][1] > 0 else f"{nb(-ecart_it[-1][1])} point de moins qu'elle.")})
    constats.append({"theme": "pente", "texte":
        f"Sur la courbe des États notés AAA, le taux à 10 ans dépasse celui à 2 ans de {nb(pente)} point : "
        + ("la courbe est pentue, les marchés exigent une prime pour prêter longtemps." if pente > 0.5 else
           "la courbe est plutôt plate, prêter à 10 ans ne rapporte guère plus qu'à 2 ans." if pente >= 0 else
           "la courbe est inversée, signal souvent associé à un ralentissement attendu.")})
    constats.append({"theme": "bce", "texte": f"Le taux de dépôt de la BCE est de {nb(bce[1])} % depuis le {date_fr(bce[0])}."})
    constats.append({"theme": "reel", "texte":
        f"Inflation en France sur un an : {nb(infl[1], 1)} % en {mois_fr(infl[0])}. Le Livret A à {nb(livret)} % rapporte donc "
        f"{nb(livret - infl[1], 1, True)} point une fois l'inflation déduite, l'OAT 10 ans {nb(fr[-1][1] - infl[1], 1, True)} point."})
    return constats
