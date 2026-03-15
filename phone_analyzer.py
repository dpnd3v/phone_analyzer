#!/usr/bin/env python3
"""
Italian Phone Number Analyzer v3.0
Uso: python phone_analyzer.py <numero>
"""

import sys
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# ── DATABASE PREFISSI FISSI ────────────────────────────────────────────────
PREFISSI_FISSI = {
    "010": ("Genova", "Liguria"),
    "011": ("Torino", "Piemonte"),
    "012": ("Cuneo/Asti", "Piemonte"),
    "013": ("Alessandria/Novara", "Piemonte"),
    "014": ("Asti/Biella", "Piemonte"),
    "015": ("Biella/Vercelli", "Piemonte"),
    "019": ("Savona", "Liguria"),
    "02":  ("Milano", "Lombardia"),
    "030": ("Brescia", "Lombardia"),
    "031": ("Como", "Lombardia"),
    "035": ("Bergamo", "Lombardia"),
    "036": ("Lecco/Sondrio", "Lombardia"),
    "039": ("Monza", "Lombardia"),
    "040": ("Trieste", "Friuli-Venezia Giulia"),
    "041": ("Venezia", "Veneto"),
    "0421":("San Donà di Piave", "Veneto"),
    "0422":("Treviso", "Veneto"),
    "045": ("Verona", "Veneto"),
    "046": ("Mantova/Gorizia", "Veneto/FVG"),
    "049": ("Padova", "Veneto"),
    "050": ("Pisa", "Toscana"),
    "051": ("Bologna", "Emilia-Romagna"),
    "052": ("Parma/Piacenza", "Emilia-Romagna"),
    "053": ("Modena/Reggio Emilia", "Emilia-Romagna"),
    "054": ("Ravenna/Forlì", "Emilia-Romagna"),
    "055": ("Firenze", "Toscana"),
    "057": ("Siena/Arezzo", "Toscana"),
    "059": ("Modena", "Emilia-Romagna"),
    "06":  ("Roma", "Lazio"),
    "070": ("Cagliari", "Sardegna"),
    "071": ("Ancona", "Marche"),
    "075": ("Perugia", "Umbria"),
    "079": ("Sassari", "Sardegna"),
    "080": ("Bari", "Puglia"),
    "081": ("Napoli", "Campania"),
    "082": ("Salerno/Avellino", "Campania"),
    "085": ("Pescara", "Abruzzo"),
    "086": ("L'Aquila/Chieti", "Abruzzo"),
    "089": ("Salerno", "Campania"),
    "090": ("Messina", "Sicilia"),
    "091": ("Palermo", "Sicilia"),
    "095": ("Catania", "Sicilia"),
    "099": ("Taranto", "Puglia"),
}

# ── DATABASE OPERATORI MOBILI ──────────────────────────────────────────────
OPERATORI_MOBILI = {
    "320": "Vodafone", "323": "Vodafone", "328": "Vodafone", "329": "Vodafone",
    "330": "Vodafone", "331": "Vodafone", "332": "Vodafone", "360": "Vodafone",
    "366": "Vodafone", "390": "Vodafone", "391": "Vodafone",
    "333": "TIM", "334": "TIM", "335": "TIM", "336": "TIM",
    "337": "TIM (storico)", "338": "TIM", "339": "TIM", "392": "TIM", "393": "TIM",
    "340": "Wind Tre", "341": "Wind Tre", "342": "Wind Tre", "343": "Wind Tre",
    "344": "Wind Tre", "345": "Wind Tre", "346": "Wind Tre", "347": "Wind Tre",
    "348": "Wind Tre", "349": "Wind Tre", "380": "Wind Tre", "383": "Wind Tre",
    "385": "Wind Tre", "388": "Wind Tre", "389": "Wind Tre", "397": "Wind Tre",
    "398": "Wind Tre", "399": "Wind Tre",
    "350": "PosteMobile", "374": "PosteMobile", "375": "PosteMobile", "376": "PosteMobile",
    "351": "Iliad", "370": "Iliad", "371": "Iliad", "373": "Iliad",
    "368": "Fastweb Mobile",
    "377": "MVNO/Operatore virtuale",
}

# ── NUMERI SPECIALI ────────────────────────────────────────────────────────
NUMERI_SPECIALI = {
    "112": ("Carabinieri / Emergenza EU", "EMERGENZA", "GRATUITO"),
    "113": ("Polizia di Stato", "EMERGENZA", "GRATUITO"),
    "115": ("Vigili del Fuoco", "EMERGENZA", "GRATUITO"),
    "116": ("Soccorso Stradale ACI", "ASSISTENZA", "A PAGAMENTO"),
    "117": ("Guardia di Finanza", "EMERGENZA", "GRATUITO"),
    "118": ("Emergenza Sanitaria", "EMERGENZA", "GRATUITO"),
    "1515": ("Emergenza Ambientale", "EMERGENZA", "GRATUITO"),
    "800": ("Numero Verde", "VERDE", "GRATUITO"),
    "803": ("Poste Italiane", "SERVIZIO", "TARIFFATO"),
    "840": ("Tariffa ridotta", "SPECIALE", "RIDOTTO"),
    "848": ("Tariffa ridotta", "SPECIALE", "RIDOTTO"),
    "199": ("Tariffa maggiorata", "PREMIUM", "MAGGIORATO"),
    "166": ("Tariffa maggiorata", "PREMIUM", "MAGGIORATO"),
    "899": ("Intrattenimento / Premium", "PREMIUM", "MOLTO ALTO"),
    "144": ("Tariffa maggiorata", "PREMIUM", "MAGGIORATO"),
    "70":  ("Servizi SMS a pagamento", "PREMIUM", "VARIABILE"),
}


# ── UTILITY ────────────────────────────────────────────────────────────────

def riga(label, valore):
    if valore is not None and valore != "":
        print(f"  {label:<22} {valore}")

def sezione(titolo):
    print(f"\n[ {titolo} ]")

def normalizza(numero: str) -> str | None:
    n = re.sub(r'[\s\-\.\(\)\/]', '', numero.strip())
    if n.startswith('+39'):   return n
    if n.startswith('0039'):  return '+39' + n[4:]
    if re.match(r'^\d{6,13}$', n): return '+39' + n
    return None

def classifica(locale: str) -> dict:
    for prefix, info in NUMERI_SPECIALI.items():
        if locale.startswith(prefix):
            return {"tipo": "SPECIALE", "sottotipo": info[1],
                    "descrizione": info[0], "tariffa": info[2],
                    "mobile": False, "fisso": False, "speciale": True}
    if locale.startswith('3') and len(locale) == 10:
        pref = locale[:3]
        op = OPERATORI_MOBILI.get(pref, "Operatore non identificato / numero portato")
        return {"tipo": "MOBILE", "operatore": op, "prefisso": pref,
                "mobile": True, "fisso": False, "speciale": False}
    if locale.startswith('0'):
        for l in [4, 3, 2]:
            p = locale[:l]
            if p in PREFISSI_FISSI:
                citta, regione = PREFISSI_FISSI[p]
                return {"tipo": "FISSO", "prefisso": p, "citta": citta,
                        "regione": regione, "mobile": False, "fisso": True, "speciale": False}
        return {"tipo": "FISSO", "prefisso": locale[:4], "citta": "N/D",
                "regione": "N/D", "mobile": False, "fisso": True, "speciale": False}
    return {"tipo": "SCONOSCIUTO", "mobile": False, "fisso": False, "speciale": False}

def valida(locale: str, cl: dict) -> dict:
    errori, avvisi = [], []
    score = 100
    if cl["mobile"]:
        if len(locale) != 10: errori.append(f"Lunghezza errata ({len(locale)} cifre, attese 10)"); score -= 40
        if "non identificato" in cl.get("operatore",""): avvisi.append("Prefisso non in DB — possibile numero portato (MNP)"); score -= 5
    elif cl["fisso"]:
        if not (6 <= len(locale) <= 11): avvisi.append(f"Lunghezza insolita ({len(locale)} cifre)"); score -= 10
    elif not cl["speciale"]:
        errori.append("Formato non riconoscibile"); score -= 50
    return {"valido": len(errori) == 0, "score": max(0, score), "errori": errori, "avvisi": avvisi}

def rischio(cl: dict, val: dict) -> dict:
    segnali, score = [], 0
    if cl.get("tipo") == "SPECIALE":
        if cl.get("sottotipo") == "PREMIUM":
            segnali.append("Numero PREMIUM — costo elevato per chi chiama"); score += 50
        if cl.get("tariffa") == "MOLTO ALTO":
            segnali.append("Numero 899 — spesso associato a servizi indesiderati"); score += 30
    if not val["valido"]:
        segnali.append("Formato non standard — possibile spoofing"); score += 30
    if not segnali:
        segnali.append("Nessun segnale di rischio rilevato")
    livello = "MOLTO ALTO" if score >= 70 else "ALTO" if score >= 40 else "MEDIO" if score >= 15 else "BASSO"
    return {"livello": livello, "score": score, "segnali": segnali}


# ── HTTP HELPER ────────────────────────────────────────────────────────────

def http_get(url: str, timeout=7) -> tuple[int, str]:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
            'Accept-Encoding': 'identity',
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cs = r.headers.get_content_charset() or 'utf-8'
            return r.status, r.read().decode(cs, errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""

def estrai(html: str, start: str, end: str) -> str | None:
    i = html.find(start)
    if i == -1: return None
    i += len(start)
    j = html.find(end, i)
    if j == -1: return None
    raw = re.sub(r'<[^>]+>', '', html[i:j]).strip()
    return raw or None

def pulisci(t: str) -> str:
    return re.sub(r'\s+', ' ', t).strip()


# ── LOOKUP ────────────────────────────────────────────────────────────────

def lookup_syncme(e164: str, locale: str) -> dict:
    r = {"fonte": "Sync.me", "nome": None, "social": [], "stato": "non trovato",
         "url": f"https://sync.me/search/?number={urllib.parse.quote(e164)}"}
    num = locale.lstrip('0')
    for url in [f"https://sync.me/search/?number=%2B39{num}",
                f"https://sync.me/search/?number={urllib.parse.quote(e164)}"]:
        st, html = http_get(url)
        r["url"] = url
        if st == 200 and html:
            for s, e in [('<span class="name">', '</span>'), ('<h1 class="name">', '</h1>'),
                         ('<div class="contact-name">', '</div>'), ('<title>', ' - Sync.Me'),
                         ('<title>', ' | Sync.Me')]:
                nome = estrai(html, s, e)
                if nome and len(nome) > 1 and nome.lower() not in ('sync.me','syncme','phone search','search results',''):
                    if not re.match(r'^\+?[\d\s\-]+$', nome):
                        r["nome"] = pulisci(nome); r["stato"] = "trovato"; break
            for pat, label in [('facebook.com','Facebook'),('linkedin.com','LinkedIn'),
                                ('twitter.com','Twitter/X'),('instagram.com','Instagram')]:
                if pat in html: r["social"].append(label)
            if r["stato"] == "trovato": break
    return r

def lookup_paginebianche(locale: str) -> dict:
    url = f"https://www.paginebianche.it/ricerca?qs={locale}&dv=on"
    r = {"fonte": "PagineBianche.it", "nome": None, "indirizzo": None,
         "localita": None, "stato": "non raggiungibile", "url": url}
    st, html = http_get(url)
    if st != 200 or not html: return r
    if re.search(r'nessun risultato|non trovato|0 risultati', html, re.IGNORECASE):
        r["stato"] = "nessun risultato"; return r
    for s, e in [('<span class="nome">', '</span>'), ('<h3 class="nome">', '</h3>'),
                 ('<span itemprop="name">', '</span>'), ('<a class="nome">', '</a>')]:
        nome = estrai(html, s, e)
        if nome and len(nome) > 2: r["nome"] = pulisci(nome); r["stato"] = "trovato"; break
    for s, e in [('<span itemprop="streetAddress">', '</span>'), ('<span class="indirizzo">', '</span>')]:
        ind = estrai(html, s, e)
        if ind: r["indirizzo"] = pulisci(ind); break
    for s, e in [('<span itemprop="addressLocality">', '</span>'), ('<span class="localita">', '</span>')]:
        loc = estrai(html, s, e)
        if loc: r["localita"] = pulisci(loc); break
    if r["stato"] == "non raggiungibile": r["stato"] = "nessun risultato"
    return r

def lookup_paginegialle(locale: str) -> dict:
    url = f"https://www.paginegialle.it/ricerca?qs={locale}&dv=on"
    r = {"fonte": "PagineGialle.it", "nome": None, "indirizzo": None,
         "localita": None, "telefono": None, "stato": "non raggiungibile", "url": url}
    st, html = http_get(url)
    if st != 200 or not html: return r
    if re.search(r'nessun risultato|non trovato|0 risultati', html, re.IGNORECASE):
        r["stato"] = "nessun risultato"; return r
    for s, e in [('<span class="nome">', '</span>'), ('<h3 class="nome">', '</h3>'),
                 ('<span itemprop="name">', '</span>'), ('<a class="nome">', '</a>'),
                 ('<h2 itemprop="name">', '</h2>')]:
        nome = estrai(html, s, e)
        if nome and len(nome) > 2: r["nome"] = pulisci(nome); r["stato"] = "trovato"; break
    for s, e in [('<span itemprop="streetAddress">', '</span>'), ('<span class="indirizzo">', '</span>')]:
        ind = estrai(html, s, e)
        if ind: r["indirizzo"] = pulisci(ind); break
    for s, e in [('<span itemprop="addressLocality">', '</span>'), ('<span class="localita">', '</span>')]:
        loc = estrai(html, s, e)
        if loc: r["localita"] = pulisci(loc); break
    if r["stato"] == "non raggiungibile": r["stato"] = "nessun risultato"
    return r


# ── REPORT ────────────────────────────────────────────────────────────────

def report(numero_input: str):
    e164 = normalizza(numero_input)
    if not e164:
        print(f"Errore: '{numero_input}' non riconoscibile come numero italiano.")
        print("Formati accettati: +393471234567 / 3471234567 / 02 1234567")
        sys.exit(1)

    locale = e164[3:]
    cl  = classifica(locale)
    val = valida(locale, cl)
    ri  = rischio(cl, val)

    if locale.startswith('02') or locale.startswith('06'):
        fmt = f"+39 {locale[:2]} {locale[2:5]} {locale[5:8]} {locale[8:]}"
    elif cl["mobile"]:
        fmt = f"+39 {locale[:3]} {locale[3:6]} {locale[6:]}"
    else:
        fmt = f"+39 {locale[:4]} {locale[4:7]} {locale[7:]}"

    print()
    print("=" * 54)
    print("  ITALIAN PHONE NUMBER ANALYZER")
    print("=" * 54)

    sezione("NUMERO")
    riga("Input",           numero_input)
    riga("E.164",           e164)
    riga("Nazionale",       locale)
    riga("Internazionale",  "00" + e164[1:])
    riga("Formato",         fmt.strip())
    riga("Analisi",         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    sezione("TIPO")
    riga("Tipo",            cl["tipo"])
    if cl.get("mobile"):
        riga("Operatore",   cl["operatore"])
        riga("Prefisso",    cl["prefisso"])
        riga("Portabilità", "MNP attiva — operatore attuale potrebbe differire")
    if cl.get("fisso"):
        riga("Prefisso",    cl["prefisso"])
        riga("Città",       cl.get("citta"))
        riga("Regione",     cl.get("regione"))
        riga("Portabilità", "FNP disponibile — area basata su prefisso originario")
    if cl.get("speciale"):
        riga("Servizio",    cl.get("descrizione"))
        riga("Categoria",   cl.get("sottotipo"))
        riga("Tariffa",     cl.get("tariffa"))

    sezione("VALIDITÀ")
    riga("Stato",           "VALIDO" if val["valido"] else "NON VALIDO")
    riga("Score struttura", f"{val['score']}/100")
    for e in val["errori"]:  riga("Errore", e)
    for a in val["avvisi"]:  riga("Avviso", a)

    sezione("RISCHIO")
    riga("Livello",         ri["livello"])
    for s in ri["segnali"]: riga("", s)

    sezione("OSINT — LOOKUP")
    print("  Interrogo le fonti...", end="", flush=True)
    rs  = lookup_syncme(e164, locale)
    rpb = lookup_paginebianche(locale)
    rpg = lookup_paginegialle(locale)
    print(" fatto.\n")

    # Nome aggregato — priorità: PagineBianche > PagineGialle > Sync.me
    nomi = []
    if rpb.get("nome"): nomi.append(("PagineBianche", rpb["nome"]))
    if rpg.get("nome"): nomi.append(("PagineGialle",  rpg["nome"]))
    if rs.get("nome"):  nomi.append(("Sync.me",       rs["nome"]))

    print("  *** NOME / INTESTATARIO ***")
    if nomi:
        for fonte, nome in nomi:
            riga(f"  {fonte}", nome)
    else:
        print("  Non trovato nelle fonti pubbliche.")

    sezione("DETTAGLIO FONTI")

    print(f"  Sync.me            [{rs['stato']}]")
    if rs.get("nome"):   riga("    Nome",   rs["nome"])
    if rs.get("social"): riga("    Social", ", ".join(rs["social"]))

    print(f"  PagineBianche.it   [{rpb['stato']}]")
    if rpb.get("nome"):      riga("    Nome",      rpb["nome"])
    if rpb.get("indirizzo"): riga("    Indirizzo", rpb["indirizzo"])
    if rpb.get("localita"):  riga("    Localita",  rpb["localita"])

    print(f"  PagineGialle.it    [{rpg['stato']}]")
    if rpg.get("nome"):      riga("    Nome",      rpg["nome"])
    if rpg.get("indirizzo"): riga("    Indirizzo", rpg["indirizzo"])
    if rpg.get("localita"):  riga("    Localita",  rpg["localita"])

    sezione("LINK")
    print(f"  Sync.me      https://sync.me/search/?number={urllib.parse.quote(e164)}")
    print(f"  PagBianche   https://www.paginebianche.it/ricerca?qs={locale}")
    print(f"  PagGialle    https://www.paginegialle.it/ricerca?qs={locale}")

    sezione("RIEPILOGO")
    riga("Numero",   e164)
    if cl.get("mobile"):
        riga("Tipo", f"MOBILE — {cl.get('operatore','')}")
    elif cl.get("fisso"):
        riga("Tipo", f"FISSO — {cl.get('citta','')}, {cl.get('regione','')}")
    else:
        riga("Tipo", cl["tipo"])
    riga("Nome",     nomi[0][1] if nomi else "N/D")
    riga("Validità", "VALIDO" if val["valido"] else "NON VALIDO")
    riga("Rischio",  ri["livello"])
    print()


# ── ENTRY POINT ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python phone_analyzer.py <numero>")
        print("Esempi:")
        print("  python phone_analyzer.py +393471234567")
        print("  python phone_analyzer.py 0212345678")
        print("  python phone_analyzer.py \"347 123 4567\"")
        print()
        print("Numero: ", end="")
        try:
            numero = input().strip()
            if not numero: sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
    else:
        numero = ' '.join(sys.argv[1:])
    report(numero)

if __name__ == "__main__":
    main()