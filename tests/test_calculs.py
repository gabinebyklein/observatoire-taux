"""Cas calculés à la main : si un de ces tests casse, l'observatoire se trompe."""
import json, pathlib
import pytest
from observatoire.obligations import prix, duration_modifiee, convexite, dv01, choc
from observatoire.analyses import ecart, plus_haut_depuis, taux_en_vigueur, taux_reels, rejouer_ecart, lecture
from observatoire.reperes import LIVRET_A


def test_une_obligation_dont_le_coupon_egale_le_taux_vaut_son_nominal():
    for taux in (1.0, 3.0, 5.5):
        assert prix(100, taux, 10, taux) == pytest.approx(100)


def test_zero_coupon():
    # 100 € dans 10 ans, actualisés à 5 % : 100 / 1,05^10 = 61,39 €
    assert prix(100, 0, 10, 5) == pytest.approx(100 / 1.05 ** 10)
    # sa duration modifiée vaut 10 / 1,05 = 9,52 ans
    assert duration_modifiee(100, 0, 10, 5) == pytest.approx(10 / 1.05)


def test_hausse_de_taux_d_un_point():
    # OAT 10 ans, coupon 3 %, le taux passe de 3 % à 4 % :
    # 3 × (1 − 1,04^−10) / 0,04 + 100 / 1,04^10 = 91,89 € : le prix baisse d'environ 8,1 %
    assert prix(100, 3, 10, 4) == pytest.approx(3 * (1 - 1.04 ** -10) / 0.04 + 100 / 1.04 ** 10)
    c = choc(100, 3, 10, 3, 1.0)
    assert c["variation_pct"] == pytest.approx(-8.11, abs=0.01)


def test_la_convexite_ameliore_l_approximation():
    c = choc(100, 3, 30, 3, 2.0)                      # gros choc sur une obligation longue
    erreur_duration = abs(c["approx_duration_pct"] - c["variation_pct"])
    erreur_convexite = abs(c["approx_duration_convexite_pct"] - c["variation_pct"])
    assert erreur_convexite < erreur_duration / 5


def test_dv01_coherent_avec_la_duration():
    # DV01 ≈ duration modifiée × prix × 0,0001
    n, c, m, y = 10_000_000, 3.5, 10, 3.5
    assert dv01(n, c, m, y) == pytest.approx(duration_modifiee(n, c, m, y) * prix(n, c, m, y) * 1e-4, rel=1e-4)


def test_ecart_et_plus_haut():
    fr = [("2024-01", 3.0), ("2024-02", 3.6), ("2024-03", 3.4), ("2024-04", 3.5)]
    de = [("2024-01", 2.5), ("2024-02", 2.6), ("2024-03", 2.6), ("2024-04", 2.6)]
    assert ecart(fr, de) == [("2024-01", 0.5), ("2024-02", 1.0), ("2024-03", 0.8), ("2024-04", 0.9)]
    assert plus_haut_depuis(ecart(fr, de)) == "2024-02"        # 0,9 : plus haut depuis février (1,0)


def test_taux_en_vigueur_du_livret_a():
    assert taux_en_vigueur(LIVRET_A, "2026-03-15") == 1.5
    assert taux_en_vigueur(LIVRET_A, "2026-11-15") == 1.7
    assert taux_en_vigueur(LIVRET_A, "2023-06") == 3.0


def test_taux_reel():
    assert taux_reels([("2026-10", 4.9)], [("2026-10", 3.8)]) == [("2026-10", 1.1)]


def test_rejouer_ecart():
    fr = [("2024-05", 3.0), ("2024-06", 3.3)]
    de = [("2024-05", 2.5), ("2024-06", 2.5)]
    r = rejouer_ecart(fr, de, "2024-05", "2024-06")
    # l'écart passe de 0,50 à 0,80 point : +30 points de base, la position (acheter OAT, vendre Bund) perd
    assert r["variation_pb"] == pytest.approx(30)
    assert r["resultat"] == pytest.approx(-30 * r["dv01"])
    assert r["resultat"] < 0


def test_lecture_sur_les_vraies_donnees():
    fichier = pathlib.Path(__file__).resolve().parent.parent / "data" / "donnees.json"
    if not fichier.exists():
        pytest.skip("données pas encore téléchargées")
    constats = lecture(json.load(open(fichier)))
    assert len(constats) == 5 and all(c["texte"] for c in constats)
