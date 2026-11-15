"""Mathématiques d'une obligation à taux fixe (coupon annuel). Utilisé par les tests et par la page web (Pyodide).

Prix = somme des flux futurs actualisés au taux du marché :
    P = C/(1+y) + C/(1+y)^2 + ... + (C + N)/(1+y)^n
C'est la même mécanique que le DCF d'une entreprise : un euro reçu plus tard vaut moins aujourd'hui."""


def flux(nominal, coupon_pct, maturite_ans):
    """[(année, montant)] : un coupon chaque année, plus le nominal remboursé à la fin."""
    c = nominal * coupon_pct / 100
    return [(t, c + (nominal if t == maturite_ans else 0)) for t in range(1, maturite_ans + 1)]


def prix(nominal, coupon_pct, maturite_ans, taux_pct):
    y = taux_pct / 100
    return sum(f / (1 + y) ** t for t, f in flux(nominal, coupon_pct, maturite_ans))


def duration_modifiee(nominal, coupon_pct, maturite_ans, taux_pct):
    """Perte en % du prix quand le taux monte d'un point (approximation au premier ordre)."""
    y = taux_pct / 100
    p = prix(nominal, coupon_pct, maturite_ans, taux_pct)
    macaulay = sum(t * f / (1 + y) ** t for t, f in flux(nominal, coupon_pct, maturite_ans)) / p
    return macaulay / (1 + y)


def convexite(nominal, coupon_pct, maturite_ans, taux_pct):
    """Courbure : corrige l'approximation de la duration pour les gros mouvements de taux."""
    y = taux_pct / 100
    p = prix(nominal, coupon_pct, maturite_ans, taux_pct)
    return sum(t * (t + 1) * f / (1 + y) ** (t + 2) for t, f in flux(nominal, coupon_pct, maturite_ans)) / p


def dv01(nominal, coupon_pct, maturite_ans, taux_pct):
    """Gain ou perte en euros pour un mouvement de taux d'un point de base (0,01 %). La mesure de risque d'un desk de taux."""
    haut = prix(nominal, coupon_pct, maturite_ans, taux_pct + 0.01)
    bas = prix(nominal, coupon_pct, maturite_ans, taux_pct - 0.01)
    return (bas - haut) / 2


def choc(nominal, coupon_pct, maturite_ans, taux_pct, variation_pts):
    """Ce que devient le prix si le taux bouge de `variation_pts` points : calcul exact et deux approximations."""
    p0 = prix(nominal, coupon_pct, maturite_ans, taux_pct)
    p1 = prix(nominal, coupon_pct, maturite_ans, taux_pct + variation_pts)
    d = duration_modifiee(nominal, coupon_pct, maturite_ans, taux_pct)
    cx = convexite(nominal, coupon_pct, maturite_ans, taux_pct)
    dy = variation_pts / 100
    return {
        "prix_avant": p0, "prix_apres": p1, "variation_pct": (p1 / p0 - 1) * 100,
        "approx_duration_pct": -d * dy * 100,
        "approx_duration_convexite_pct": (-d * dy + 0.5 * cx * dy ** 2) * 100,
        "duration_modifiee": d, "convexite": cx, "dv01": dv01(nominal, coupon_pct, maturite_ans, taux_pct),
    }
