# Challenge 1: The Stories

## Contesto

Brennero Logistics S.p.A. gestisce un portale ordini interno usato da operatori, magazzinieri e management. Il sistema attuale è un monolite Java/Servlet del 2015, senza documentazione aggiornata. Il board ha approvato un progetto di "modernizzazione" che include: ampliamento del catalogo prodotti, arricchimento dell'anagrafica clienti, dashboard moderna con grafici, migrazione da Java a Python, e ottimizzazione del database.

Questo documento definisce le user story per le business capability **esistenti e da evolvere**, con acceptance criteria eseguibili da un tester. Le priorità riflettono i disaccordi tra stakeholder, documentati esplicitamente.

---

## Stakeholder e priorità in conflitto

| Stakeholder | Priorità dichiarata | Motivazione |
|---|---|---|
| **Operations (Resp. Logistica)** | Catalogo servizi più ricco, tracking affidabile | "Ci servono tipologie prodotto diverse: trasporti, dogana, magazzino, assicurazioni. Oggi è tutto mischiato." |
| **Finance (CFO)** | Totali coerenti, dashboard per il board | "Servono grafici chiari, non tabelle HTML. Il board vuole trend e KPI a colpo d'occhio." |
| **Warehouse (Resp. Magazzino)** | Giacenze allineate, catalogo materiali | "Devo distinguere servizi da materiali fisici. Solo i materiali hanno giacenza." |
| **IT (CTO)** | Migrazione a Python, sicurezza, manutenibilità | "Java/Servlet del 2015 è insostenibile. Python con un framework moderno ci permette di iterare 3x più veloce." |
| **Management (CEO)** | Zero downtime, dati storici preservati | "Il portale non può fermarsi. E non perdiamo gli ordini degli ultimi 10 anni." |
| **Sales (Resp. Commerciale)** | Classificazione clienti per priorità | "Ho bisogno di sapere subito chi sono i clienti Gold, Silver e Bronze. Oggi devo aprire ogni scheda." |
| **Customer Service** | Ricerca rapida per nome cliente o prodotto | "Perdo 5 minuti a cercare un cliente. Mi serve una barra di ricerca che funzioni." |

### Disaccordi espliciti

1. **Finance vs Operations**: Finance vuole bloccare la creazione ordini finché i totali non sono corretti. Operations dice "spediamo prima, sistemiamo dopo" perché i ritardi costano penali.
2. **IT vs Management**: IT vuole riscrivere tutto in Python. Management chiede zero downtime e compatibilità con i dati storici.
3. **Warehouse vs Operations**: Warehouse chiede di distinguere servizi (senza giacenza) da materiali (con giacenza). Operations non vuole complicare il form ordine.
4. **Sales vs IT**: Sales vuole la classificazione clienti subito. IT dice che prima va migrata l'anagrafica al nuovo stack.

---

## Epic 1: Gestione Ordini — Catalogo Servizi e Materiali

> **Obiettivo:** Ampliare il catalogo prodotti con tipologie differenti (servizi di trasporto, pratiche doganali, materiali di magazzino, assicurazioni, consulenza) per supportare offerte commerciali più articolate.

### US-1.1: Visualizzazione lista ordini con filtri

**Come** operatore logistico  
**Voglio** vedere la lista degli ordini filtrata per cliente, stato, periodo e tipologia prodotto  
**In modo da** trovare rapidamente gli ordini su cui devo agire

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | La lista mostra: numero ordine, cliente, data, consegna prevista, stato, importo | Aprire `/orders` → verificare che tutte le colonne siano presenti |
| AC-2 | Il filtro per cliente cerca per ragione sociale (match parziale) | Inserire "Alpini" nel campo cliente → solo ordini di "Trasporti Alpini" visibili |
| AC-3 | Il filtro per stato mostra solo gli ordini in quello stato | Selezionare "Consegnato" → verificare che tutti i risultati abbiano stato "Consegnato" |
| AC-4 | Il filtro per data filtra su DATA_ORDINE nel range [da, a] | Inserire da=2024-02-01, a=2024-02-28 → solo ordini di febbraio 2024 |
| AC-5 | Senza filtri, tutti gli ordini sono visibili ordinati per data decrescente | Caricare la pagina senza parametri → ordine più recente è il primo |
| AC-6 | Gli stati sono tutti mappati con etichetta leggibile (nessun codice numerico esposto) | Nessun ordine mostra un numero grezzo come stato |

**Priorità:** MUST

---

### US-1.2: Catalogo prodotti con categorie e tipologie

**Come** operatore commerciale  
**Voglio** un catalogo prodotti organizzato per tipologia (Servizi di Trasporto, Dogana, Magazzino, Assicurazioni, Consulenza)  
**In modo da** comporre ordini con offerte diversificate

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Ogni prodotto ha una tipologia: TRASPORTO, DOGANA, MAGAZZINO, ASSICURAZIONE, CONSULENZA | Query: `SELECT DISTINCT TIPOLOGIA FROM PRODOTTI` → 5 valori |
| AC-2 | I servizi (TRASPORTO, DOGANA, ASSICURAZIONE, CONSULENZA) non hanno giacenza | Prodotti con tipologia servizio → GIACENZA = NULL o non mostrata |
| AC-3 | I materiali (MAGAZZINO) hanno giacenza tracciata | Prodotti con tipologia MAGAZZINO → GIACENZA visibile e decrementata all'ordine |
| AC-4 | Il catalogo è consultabile con filtro per tipologia | Pagina catalogo → dropdown tipologia → filtro funzionante |
| AC-5 | Ogni prodotto ha: codice, descrizione, tipologia, unità di misura, prezzo unitario, IVA | Verificare tutti i campi nella scheda prodotto |
| AC-6 | Il catalogo contiene almeno 15 prodotti distribuiti sulle 5 tipologie | Query: `SELECT TIPOLOGIA, COUNT(*) FROM PRODOTTI GROUP BY TIPOLOGIA` → min 2 per tipologia |

**Priorità:** MUST

**Catalogo di riferimento:**

| Tipologia | Esempi prodotto |
|---|---|
| TRASPORTO | Trasporto nazionale, internazionale EU, extra-EU, espresso, groupage, full truck |
| DOGANA | Pratica doganale import, export, triangolazione, deposito doganale |
| MAGAZZINO | Stoccaggio pallet/mese, picking & packing, etichettatura, cross-docking |
| ASSICURAZIONE | Assicurazione merce base, all-risk, responsabilità vettoriale |
| CONSULENZA | Consulenza logistica, audit supply chain, formazione operatori |

---

### US-1.3: Creazione ordine con catalogo ampliato

**Come** operatore  
**Voglio** creare un nuovo ordine selezionando prodotti da diverse tipologie  
**In modo da** comporre ordini misti (es. trasporto + dogana + assicurazione)

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Il form mostra i prodotti raggruppati per tipologia | Aprire nuovo ordine → prodotti organizzati in sezioni/tabs per tipologia |
| AC-2 | È possibile aggiungere prodotti di tipologie diverse nello stesso ordine | Creare ordine con 1 prodotto TRASPORTO + 1 DOGANA + 1 ASSICURAZIONE → ordine valido |
| AC-3 | L'ordine viene creato con stato "Bozza" | Creare ordine → stato = "Bozza" |
| AC-4 | Il numero ordine segue il formato ORD-YYYY-NNNN | Creare ordine → numero conforme |
| AC-5 | La consegna prevista è calcolata automaticamente a +7 giorni | Creare ordine → consegna prevista = oggi + 7 |
| AC-6 | Lo sconto cliente è applicato uniformemente a tutte le righe | Creare ordine per cliente con sconto 5% → ogni riga scontata del 5% |
| AC-7 | Solo i prodotti MAGAZZINO decrementano la giacenza | Creare ordine misto → solo prodotti MAGAZZINO hanno decremento giacenza |

**Priorità:** MUST

---

### US-1.4: Aggiornamento stato ordine con workflow

**Come** operatore logistico  
**Voglio** aggiornare lo stato di un ordine seguendo transizioni valide  
**In modo da** tracciare l'avanzamento senza errori

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Le transizioni valide sono: Bozza→Confermato→In Lavorazione→Spedito→Consegnato | Tentare transizione Bozza→Spedito → bloccata |
| AC-2 | Lo stato "Annullato" è raggiungibile da Bozza e Confermato, non da stati successivi | Tentare annullamento da "Spedito" → bloccato |
| AC-3 | Il cambio stato viene registrato con utente e timestamp | Aggiornare stato → MODIFIED_BY e MODIFIED_DATE aggiornati |
| AC-4 | Quando lo stato passa a "Consegnato", la data consegna effettiva viene impostata | Impostare stato "Consegnato" → DATA_CONSEGNA_EFFETTIVA = now |
| AC-5 | Il dropdown mostra solo le transizioni valide dallo stato corrente | Ordine in stato "In Lavorazione" → dropdown mostra solo "Spedito" e non "Bozza" |

**Priorità:** MUST

---

## Epic 2: Gestione Clienti — Anagrafica Arricchita e Classificazione

> **Obiettivo:** Arricchire l'anagrafica clienti con campi aggiuntivi, implementare ricerca avanzata (per nome cliente o prodotto), e classificare i clienti con priorità (Gold/Silver/Bronze).

### US-2.1: Anagrafica cliente estesa

**Come** operatore commerciale  
**Voglio** gestire un'anagrafica cliente completa con tutti i dati necessari  
**In modo da** avere un quadro completo del cliente senza consultare altri sistemi

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | L'anagrafica include i campi base: ragione sociale, P.IVA, codice fiscale, indirizzo, CAP, città, provincia, telefono, email | Aprire scheda cliente → tutti i campi presenti |
| AC-2 | Campi aggiuntivi: PEC, codice SDI, settore merceologico, referente commerciale, telefono referente | Verificare campi aggiuntivi nella scheda |
| AC-3 | Il campo "note commerciali" è editabile (testo libero) | Inserire nota → salvataggio corretto |
| AC-4 | La data ultimo ordine è calcolata automaticamente | Verificare che corrisponda all'ordine più recente del cliente |
| AC-5 | Il fatturato annuo è calcolato automaticamente (somma ordini non annullati dell'anno) | Verificare coerenza con il report |

**Priorità:** MUST

---

### US-2.2: Classificazione clienti per priorità

**Come** responsabile commerciale  
**Voglio** classificare i clienti in 3 livelli di priorità (Gold, Silver, Bronze)  
**In modo da** differenziare il servizio e le condizioni commerciali

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Ogni cliente ha un campo "Classificazione" con valori: Gold (1), Silver (2), Bronze (3) | Aprire scheda cliente → campo classificazione presente |
| AC-2 | La classificazione è visibile nella lista clienti con badge colorato | Lista clienti → badge Gold (oro), Silver (argento), Bronze (bronzo) |
| AC-3 | La classificazione è editabile dall'operatore | Cambiare classificazione → salvataggio corretto |
| AC-4 | La lista clienti è filtrabile per classificazione | Filtro "Solo Gold" → solo clienti Gold visibili |
| AC-5 | Il dettaglio ordine mostra la classificazione del cliente | Aprire dettaglio ordine → badge classificazione cliente visibile |

**Priorità:** MUST

---

### US-2.3: Ricerca avanzata clienti e prodotti

**Come** operatore  
**Voglio** una barra di ricerca che cerchi sia per nome cliente che per nome prodotto  
**In modo da** trovare velocemente ciò che mi serve senza navigare tra menu diversi

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Esiste una barra di ricerca globale accessibile da ogni pagina (header) | Verificare presenza search bar nel header di navigazione |
| AC-2 | Cercando un nome cliente, i risultati mostrano i clienti corrispondenti | Cercare "Alpini" → risultato "Trasporti Alpini S.r.l." |
| AC-3 | Cercando un nome prodotto, i risultati mostrano i prodotti corrispondenti | Cercare "Trasporto" → risultati prodotti di tipologia TRASPORTO |
| AC-4 | I risultati sono raggruppati per tipo (Clienti / Prodotti) | Cercare "Alpini" → sezione "Clienti" con risultati, sezione "Prodotti" vuota o con match |
| AC-5 | Click su un risultato cliente apre la scheda cliente | Click su "Trasporti Alpini" → pagina dettaglio cliente |
| AC-6 | Click su un risultato prodotto apre la scheda prodotto nel catalogo | Click su "Trasporto Nazionale" → dettaglio prodotto |
| AC-7 | La ricerca è case-insensitive e supporta match parziale | Cercare "alpini" (minuscolo) → trova "Trasporti Alpini" |

**Priorità:** MUST

---

## Epic 3: Reportistica — Dashboard Moderna

> **Obiettivo:** Sostituire i report tabellari con una dashboard interattiva con grafici, KPI e visualizzazioni moderne.

### US-3.1: Dashboard KPI

**Come** manager  
**Voglio** una dashboard con indicatori chiave a colpo d'occhio  
**In modo da** monitorare l'andamento del business senza scaricare report

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Card KPI visibili: Ordini totali, Fatturato totale, Ordini in corso, Ticket medio | Dashboard → 4 card KPI nella parte superiore |
| AC-2 | I KPI filtrano per anno (default: anno corrente) | Cambiare anno → KPI aggiornati |
| AC-3 | Ogni card mostra variazione % rispetto al periodo precedente (se dati disponibili) | KPI fatturato mostra "+12%" o "−5%" rispetto all'anno prima |
| AC-4 | Gli ordini annullati sono esclusi da fatturato e ticket medio | Verificare coerenza escludendo stato 5 |

**Priorità:** MUST

---

### US-3.2: Grafico fatturato per cliente (bar chart)

**Come** manager  
**Voglio** un grafico a barre del fatturato per cliente  
**In modo da** identificare i clienti più importanti visivamente

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Grafico a barre orizzontali: asse X = fatturato, asse Y = clienti | Dashboard → grafico presente e leggibile |
| AC-2 | I clienti sono ordinati per fatturato decrescente | Il cliente con il fatturato maggiore è in cima |
| AC-3 | Hover su barra mostra tooltip con: cliente, numero ordini, fatturato totale | Hover → tooltip con dati corretti |
| AC-4 | Le barre sono colorate per classificazione cliente (Gold/Silver/Bronze) | Barre Gold = colore oro, Silver = argento, Bronze = bronzo |

**Priorità:** SHOULD

---

### US-3.3: Grafico andamento ordini nel tempo (line chart)

**Come** manager  
**Voglio** un grafico a linee che mostri l'andamento degli ordini per mese  
**In modo da** identificare trend e stagionalità

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Grafico a linee: asse X = mesi, asse Y = numero ordini | Dashboard → grafico presente |
| AC-2 | Una seconda linea mostra il fatturato per mese | Due linee distinguibili (ordini e fatturato) |
| AC-3 | Filtro per anno | Cambiare anno → grafico aggiornato |
| AC-4 | Hover su punto mostra: mese, numero ordini, fatturato | Tooltip con dati corretti |

**Priorità:** SHOULD

---

### US-3.4: Grafico distribuzione stati ordini (pie/donut chart)

**Come** responsabile logistica  
**Voglio** un grafico a torta della distribuzione degli ordini per stato  
**In modo da** capire quanti ordini sono in coda, in lavorazione o completati

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Grafico donut con segmenti per ogni stato (Bozza, Confermato, In Lavorazione, Spedito, Consegnato, Annullato) | Dashboard → grafico presente |
| AC-2 | Ogni segmento mostra il conteggio e la percentuale | Hover/label → es. "Consegnato: 3 (33%)" |
| AC-3 | I colori sono semantici (es. verde=Consegnato, rosso=Annullato, giallo=In Lavorazione) | Colori coerenti con lo stato |

**Priorità:** SHOULD

---

## Epic 4: Modernizzazione — Migrazione Java → Python

> **Obiettivo:** Riscrivere il portale da Java/Servlet a Python (framework moderno), risolvendo le anomalie note del monolite originale: SQL injection, password in chiaro, God class, dipendenze circolari, assenza di transazioni.

### US-4.1: Applicazione Python con framework web moderno

**Come** sviluppatore  
**Voglio** che il portale sia riscritto in Python con un framework moderno (Flask/FastAPI)  
**In modo da** avere un codebase manutenibile, testabile e sicuro

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | L'applicazione Python serve tutte le pagine funzionanti del portale Java | Tutte le action (orders, orderDetail, newOrder, saveOrder, updateStatus, report, customers, login, logout) funzionano |
| AC-2 | L'architettura segue il pattern MVC/MTV con separazione responsabilità | Nessun "God class": route separate, model layer, template layer |
| AC-3 | Il database è lo stesso (H2 o SQLite per sviluppo, schema compatibile) | Lo schema SQL è compatibile con i dati esistenti |
| AC-4 | L'applicazione si avvia con un singolo comando (`python app.py` o `flask run`) | Esecuzione comando → portale accessibile su localhost |

**Priorità:** MUST

---

### US-4.2: Risoluzione anomalie di sicurezza

**Come** CTO  
**Voglio** che tutte le vulnerabilità note del monolite Java siano risolte  
**In modo da** superare un audit di sicurezza

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Nessuna SQL injection: tutte le query usano parametri preparati | Grep codebase: nessuna concatenazione di stringhe in query SQL |
| AC-2 | Password memorizzate con hash sicuro (bcrypt o argon2) | Query DB: campo password contiene hash, non testo in chiaro |
| AC-3 | Protezione CSRF su tutti i form POST | Ogni form ha token CSRF, POST senza token → errore 403 |
| AC-4 | Sessioni sicure con timeout | Sessione scade dopo 30 minuti di inattività |
| AC-5 | Input validation su tutti i campi utente | Inserire `<script>alert(1)</script>` in un campo → input sanitizzato |
| AC-6 | HTTP security headers presenti (X-Content-Type-Options, X-Frame-Options, CSP) | Verificare headers nelle response HTTP |

**Priorità:** MUST

---

### US-4.3: Risoluzione anomalie architetturali

**Come** sviluppatore  
**Voglio** che i problemi strutturali del monolite siano risolti  
**In modo da** avere un codebase estendibile

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Nessuna dipendenza circolare tra moduli | Analisi import → nessun ciclo |
| AC-2 | Le operazioni su ordini usano transazioni database | Creare ordine con errore a metà → rollback completo, nessun dato parziale |
| AC-3 | La logica di calcolo sconto è centralizzata e documentata | Un solo punto dove lo sconto viene applicato, regola documentata |
| AC-4 | Gli stati ordine sono definiti come Enum, non numeri magici | Grep codebase: nessun numero hardcodato per gli stati |
| AC-5 | La gestione errori è strutturata (logging, messaggi utente, no stacktrace in UI) | Provocare errore → log file aggiornato, UI mostra messaggio generico |

**Priorità:** MUST

---

## Epic 5: Integrità Dati — Verifica, Ottimizzazione DB e Storicizzazione

> **Obiettivo:** Implementare un sistema di verifica integrità dati, ottimizzare lo schema del database, e creare un meccanismo di storicizzazione degli ordini vecchi.

### US-5.1: Coerenza totali ordine

**Come** controller finanziario  
**Voglio** che il totale in testata ordine corrisponda sempre alla somma delle righe  
**In modo da** produrre report affidabili per il board

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Per ogni ordine: IMPORTO_TOTALE = Σ(IMPORTO_RIGA) delle righe associate | Query di verifica → risultato vuoto (nessuna discrepanza) |
| AC-2 | L'importo riga = quantità × prezzo unitario × (1 - sconto/100) | Per ogni riga, verificare la formula |
| AC-3 | Un job di verifica automatica segnala discrepanze | Eseguire job → report delle incongruenze (se presenti) |

**Priorità:** MUST

---

### US-5.2: Ottimizzazione schema database

**Come** DBA  
**Voglio** uno schema database pulito e ottimizzato  
**In modo da** avere performance migliori e dati coerenti

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Campo duplicato QTA_MAGAZZINO rimosso, un solo campo GIACENZA | Schema → nessun campo QTA_MAGAZZINO |
| AC-2 | Foreign key esplicite tra tabelle (ORDINI→CLIENTI, RIGHE_ORDINE→ORDINI, RIGHE_ORDINE→PRODOTTI) | Schema → FK presenti con ON DELETE/UPDATE appropriate |
| AC-3 | Indici sulle colonne di ricerca frequente (STATO, DATA_ORDINE, ID_CLIENTE, RAGIONE_SOCIALE) | Schema → indici presenti |
| AC-4 | Campo IVA standardizzato con valori validi (22, 10, 4, 0) tramite CHECK constraint | Tentare INSERT con IVA=99 → errore |
| AC-5 | Trigger morto (TRG_CALCOLA_TOTALE) rimosso, logica nel codice applicativo | Schema → nessun trigger |

**Priorità:** MUST

---

### US-5.3: Storicizzazione ordini

**Come** responsabile IT  
**Voglio** che gli ordini più vecchi di 2 anni siano spostati in tabelle di archivio  
**In modo da** mantenere le tabelle operative snelle senza perdere dati storici

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Esistono tabelle ORDINI_ARCHIVIO e RIGHE_ORDINE_ARCHIVIO con stessa struttura | Schema → tabelle presenti |
| AC-2 | Un job di archiviazione sposta ordini con DATA_ORDINE > 2 anni e stato finale (Consegnato/Annullato) | Eseguire job → ordini vecchi spostati |
| AC-3 | Gli ordini archiviati non sono visibili nella lista ordini operativa | Lista ordini → nessun ordine archiviato |
| AC-4 | Gli ordini archiviati sono consultabili in una sezione "Archivio" dedicata | Menu "Archivio" → ordini storici visibili |
| AC-5 | Il report include sia dati operativi che archiviati | Report annuale → dati completi indipendentemente dalla storicizzazione |
| AC-6 | L'archiviazione è reversibile (un ordine può essere ripristinato) | Ripristinare ordine dall'archivio → torna nella tabella operativa |

**Priorità:** SHOULD

---

## Riepilogo priorità (MoSCoW)

| ID | Story | MUST | SHOULD | COULD |
|---|---|---|---|---|
| US-1.1 | Lista ordini con filtri | ✓ | | |
| US-1.2 | Catalogo servizi e materiali | ✓ | | |
| US-1.3 | Creazione ordine con catalogo ampliato | ✓ | | |
| US-1.4 | Stato ordine con workflow | ✓ | | |
| US-2.1 | Anagrafica cliente estesa | ✓ | | |
| US-2.2 | Classificazione clienti (Gold/Silver/Bronze) | ✓ | | |
| US-2.3 | Ricerca avanzata clienti e prodotti | ✓ | | |
| US-3.1 | Dashboard KPI | ✓ | | |
| US-3.2 | Grafico fatturato per cliente | | ✓ | |
| US-3.3 | Grafico andamento ordini nel tempo | | ✓ | |
| US-3.4 | Grafico distribuzione stati | | ✓ | |
| US-4.1 | Applicazione Python | ✓ | | |
| US-4.2 | Risoluzione anomalie sicurezza | ✓ | | |
| US-4.3 | Risoluzione anomalie architetturali | ✓ | | |
| US-5.1 | Coerenza totali ordine | ✓ | | |
| US-5.2 | Ottimizzazione schema DB | ✓ | | |
| US-5.3 | Storicizzazione ordini | | ✓ | |

---

## Decisioni pendenti

| # | Decisione | Owner | Deadline | Impatto |
|---|---|---|---|---|
| D-1 | Framework Python: Flask vs FastAPI vs Django | IT (Chiara + Lucia) | Sprint 1 | US-4.1 |
| D-2 | DB target: SQLite (dev) + PostgreSQL (prod) o mantenere H2? | IT + DBA | Sprint 1 | US-5.2 |
| D-3 | Libreria grafici: Chart.js vs Plotly vs D3.js | Dev + Finance | Sprint 1 | US-3.x |
| D-4 | Regola unica per applicazione sconto cliente (riga vs ordine) | Finance + Operations | Sprint 1 | US-1.3 |
| D-5 | Soglia temporale per storicizzazione (2 anni? 3 anni?) | Management + Finance | Sprint 2 | US-5.3 |
| D-6 | Strategia migrazione dati dal monolite Java al nuovo Python | IT | Sprint 1 | US-4.1, US-5.x |
