"""Récupère les données publiques officielles. Uniquement des sources ouvertes et réutilisables :
  BCE (Data Portal)  : courbe des taux de la zone euro, taux de dépôt  https://data.ecb.europa.eu
  Eurostat           : taux à 10 ans par pays (critère de convergence de Maastricht), inflation  https://ec.europa.eu/eurostat
Les indices TEC de la Banque de France ne sont pas utilisés : leur redistribution n'est pas autorisée."""
import csv, io, json, ssl, urllib.request

try:                                    # certificats à jour si le paquet certifi est installé
    import certifi
    CONTEXTE = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CONTEXTE = ssl.create_default_context()

BCE = "https://data-api.ecb.europa.eu/service/data"
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
ENTETES = {"User-Agent": "observatoire-taux (projet pedagogique)"}


def telecharger(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=ENTETES), timeout=120, context=CONTEXTE) as r:
        return r.read().decode("utf-8")


def serie_bce(cle, depuis=None):
    """Une série de la BCE -> [(date, valeur)]. Exemple de clé : 'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y'."""
    url = f"{BCE}/{cle}?format=csvdata&detail=dataonly" + (f"&startPeriod={depuis}" if depuis else "")
    lignes = csv.DictReader(io.StringIO(telecharger(url)))
    return [(l["TIME_PERIOD"], round(float(l["OBS_VALUE"]), 4)) for l in lignes if l["OBS_VALUE"]]


def eurostat(jeu, pays, depuis, **filtres):
    """Une série mensuelle Eurostat par pays -> {pays: [(mois, valeur)]} (format JSON-stat)."""
    params = [f"geo={p}" for p in pays] + [f"{k}={v}" for k, v in filtres.items()] + [f"sinceTimePeriod={depuis}"]
    d = json.loads(telecharger(f"{EUROSTAT}/{jeu}?" + "&".join(params)))
    ids, tailles = d["id"], d["size"]
    index = {dim: d["dimension"][dim]["category"]["index"] for dim in ids}
    temps = sorted(index["time"], key=index["time"].get)
    resultat = {}
    for p in pays:
        serie = []
        for t in temps:
            # position à plat dans le cube JSON-stat (dimensions dans l'ordre de d["id"], une seule valeur ailleurs)
            pos, facteur = 0, 1
            for dim, taille in reversed(list(zip(ids, tailles))):
                code = {"geo": p, "time": t}.get(dim)
                pos += (index[dim][code] if code is not None else 0) * facteur
                facteur *= taille
            v = d["value"].get(str(pos))
            if v is not None:
                serie.append((t, v))
        resultat[p] = serie
    return resultat


def taux_10_ans_eurostat(pays, depuis="1993-01"):
    """Taux à 10 ans des emprunts d'État, moyenne mensuelle (critère de convergence de Maastricht)."""
    return eurostat("irt_lt_mcby_m", pays, depuis)


def inflation_eurostat(pays, depuis="1997-01"):
    """Inflation sur un an (indice des prix harmonisé, nomenclature 2026)."""
    return eurostat("prc_hicp_minr", pays, depuis, unit="RCH_A", coicop18="TOTAL")
