"""Télécharge les données officielles et écrit data/donnees.json. Lancé chaque soir de semaine par GitHub Actions."""
import datetime, json, pathlib
from . import sources, reperes

RACINE = pathlib.Path(__file__).resolve().parent.parent
MATURITES = ["3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y"]
COURBE = "YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_{}"       # courbe zéro-coupon des États de la zone euro notés AAA


def a_la_date(serie, date):
    """Dernière valeur connue à cette date (ou avant)."""
    avant = [v for d, v in serie if d <= date]
    return avant[-1] if avant else None


def changements(serie):
    """Série quotidienne -> seulement les jours où la valeur change (taux directeur)."""
    sortie = []
    for d, v in serie:
        if not sortie or sortie[-1][1] != v:
            sortie.append((d, v))
    return sortie


def hebdomadaire(serie, jours_complets=730):
    """Allège l'historique : une valeur par semaine, sauf les deux dernières années gardées au jour le jour."""
    limite = str(datetime.date.fromisoformat(serie[-1][0]) - datetime.timedelta(days=jours_complets))
    garde, semaine = [], None
    for d, v in serie:
        s = datetime.date.fromisoformat(d).isocalendar()[:2]
        if d >= limite or s != semaine:
            garde.append((d, v))
        semaine = s
    return garde


def main():
    courbes = {m: sources.serie_bce(COURBE.format(m)) for m in MATURITES}
    derniere = courbes["10Y"][-1][0]
    fin = datetime.date.fromisoformat(derniere)
    dates = {"aujourd_hui": derniere,
             "il_y_a_1_an": str(fin.replace(year=fin.year - 1)),
             "il_y_a_3_ans": str(fin.replace(year=fin.year - 3))}
    instantanes = {nom: {m: a_la_date(courbes[m], d) for m in MATURITES} for nom, d in dates.items()}
    pente = [(d, round(v10 - v2, 4)) for (d, v10), (_, v2) in zip(courbes["10Y"], courbes["2Y"])]

    dix_ans = sources.taux_10_ans_eurostat(["FR", "DE", "IT", "ES"])
    donnees = {
        "mis_a_jour": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "courbe": {"maturites": MATURITES, "dates": dates, "taux": instantanes},
        "pente_2_10": hebdomadaire(pente),
        "dix_ans": dix_ans,
        "taux_depot_bce": changements(sources.serie_bce("FM/D.U2.EUR.4F.KR.DFR.LEV", "1999-01-01")),
        "inflation": {("zone_euro" if k == "EA" else k): v for k, v in sources.inflation_eurostat(["FR", "EA"]).items()},
        "livret_a": reperes.LIVRET_A, "fonds_euros": reperes.FONDS_EUROS, "evenements": reperes.EVENEMENTS,
        "sources": {
            "Courbe des taux AAA, taux de dépôt": "Banque centrale européenne, data.ecb.europa.eu",
            "Inflation (indice des prix harmonisé)": "Eurostat, prc_hicp_minr",
            "Taux à 10 ans par pays": "Eurostat, irt_lt_mcby_m (critère de convergence)",
            "Livret A": "service-public.gouv.fr / Banque de France", "Fonds euros": "ACPR (Banque de France)",
        },
    }
    sortie = RACINE / "data" / "donnees.json"
    sortie.write_text(json.dumps(donnees, ensure_ascii=False, separators=(",", ":")))
    print(f"{sortie.name} : courbe au {derniere}, 10 ans par pays jusqu'à {dix_ans['FR'][-1][0]}, "
          f"{sortie.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    main()
