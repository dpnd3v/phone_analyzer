# Italian Phone Number Analyzer

Analisi automatica di numeri di telefono italiani tramite lookup multi-fonte.

---

## Requisiti

- Python 3.10+
- Nessuna dipendenza esterna

---

## Installazione

```bash
git clone <repo>
cd phone-analyzer
```

Nessun `pip install` richiesto.

---

## Utilizzo

```bash
python phone_analyzer.py <numero>
```

**Formati accettati:**

```bash
python phone_analyzer.py +393471234567
python phone_analyzer.py 3471234567
python phone_analyzer.py "347 123 4567"
python phone_analyzer.py 0212345678
python phone_analyzer.py "02 1234 5678"
python phone_analyzer.py 0039065551234
```

**Modalità interattiva** (senza argomenti):

```bash
python phone_analyzer.py
Numero: 347 123 4567
```

---

## Output

Il report è diviso in sezioni:

| Sezione | Contenuto |
|---|---|
| `NUMERO` | Normalizzazione in E.164, formato nazionale, internazionale e leggibile |
| `TIPO` | Mobile / Fisso / Speciale, operatore o area geografica, portabilità |
| `VALIDITÀ` | Score strutturale 0–100, errori e avvisi di formato |
| `RISCHIO` | Livello (BASSO / MEDIO / ALTO / MOLTO ALTO), segnali rilevati |
| `OSINT — LOOKUP` | Interrogazione automatica delle tre fonti, nome/intestatario aggregato |
| `DETTAGLIO FONTI` | Risultato per ciascuna fonte con nome, indirizzo, social collegati |
| `LINK` | URL diretti per verifica manuale nel browser |
| `RIEPILOGO` | Cinque righe: numero, tipo, nome, validità, rischio |

---

## Fonti OSINT

| Fonte | Tipo | Ottimale per |
|---|---|---|
| **Sync.me** | Crowdsourced (rubriche + social) | Mobili con profilo social pubblico |
| **PagineBianche.it** | Elenco telefonico ufficiale | Fissi privati e attività |
| **PagineGialle.it** | Directory commerciale | Aziende e professionisti |

La priorità di aggregazione del nome è: PagineBianche → PagineGialle → Sync.me.

---

## Classificazione numeri

**Mobile** — prefissi `3xx`, 10 cifre. Operatori riconosciuti: TIM, Vodafone, Wind Tre, Iliad, PosteMobile, Fastweb Mobile, MVNO.

**Fisso** — prefissi `0xx`. Mappatura città/regione su oltre 40 prefissi geografici AGCOM.

**Speciale** — numeri di emergenza (112, 113, 115, 117, 118), numeri verdi (800), servizi a tariffa ridotta (840, 848), premium (199, 899) e altri servizi.

---

## Esempi di output

```
======================================================
  ITALIAN PHONE NUMBER ANALYZER
======================================================

[ NUMERO ]
  Input                  +393471234567
  E.164                  +393471234567
  Nazionale              3471234567
  Formato                +39 347 123 4567

[ TIPO ]
  Tipo                   MOBILE
  Operatore              Wind Tre
  Prefisso               347
  Portabilità            MNP attiva — operatore attuale potrebbe differire

[ VALIDITÀ ]
  Stato                  VALIDO
  Score struttura        100/100

[ RISCHIO ]
  Livello                BASSO
                         Nessun segnale di rischio rilevato

[ OSINT — LOOKUP ]
  Interrogo le fonti... fatto.

  *** NOME / INTESTATARIO ***
  Non trovato nelle fonti pubbliche.

[ RIEPILOGO ]
  Numero                 +393471234567
  Tipo                   MOBILE — Wind Tre
  Nome                   N/D
  Validità               VALIDO
  Rischio                BASSO
```

---

## Note

- L'operatore mostrato per i numeri mobili è quello **originario del prefisso**. La Number Portability Mobile (MNP) è attiva in Italia dal 2002: il numero potrebbe essere stato trasferito su un altro operatore.
- Per i fissi, città e regione si basano sul **prefisso originario**; la Fixed Number Portability (FNP) potrebbe aver spostato il numero su un altro operatore o area.
- I nomi restituiti da Sync.me provengono da **rubriche condivise dagli utenti** o da profili social pubblici, non da registri riservati degli operatori telefonici. L'accuratezza non è garantita.
- Le fonti web potrebbero non essere raggiungibili in ambienti con restrizioni di rete (proxy, firewall, sandbox). In questo caso le sezioni OSINT mostreranno `non raggiungibile` e i link manuali resteranno comunque disponibili.

---

## Licenza

MIT
