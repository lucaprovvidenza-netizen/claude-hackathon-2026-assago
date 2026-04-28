# Challenge 1: The Stories

## Contesto

Brennero Logistics S.p.A. gestisce un portale ordini interno usato da operatori, magazzinieri e management. Il sistema attuale è un monolite Java/Servlet del 2015, senza documentazione aggiornata. Il board ha approvato un progetto di "modernizzazione" senza definirne il perimetro.

Questo documento definisce le user story per le business capability **esistenti e critiche**, con acceptance criteria eseguibili da un tester. Le priorità riflettono i disaccordi tra stakeholder, documentati esplicitamente.

---

## Stakeholder e priorità in conflitto

| Stakeholder | Priorità dichiarata | Motivazione |
|---|---|---|
| **Operations (Resp. Logistica)** | Tracking spedizioni, stati ordine affidabili | "Se un ordine è in stato 7 nessuno sa cosa significa. Perdiamo ore al telefono." |
| **Finance (CFO)** | Totali ordine coerenti, report accurati | "Il totale in testata non coincide con la somma righe. I report al board sono inaffidabili." |
| **Warehouse (Resp. Magazzino)** | Giacenze allineate | "Ci sono due campi giacenza (GIACENZA e QTA_MAGAZZINO). Quale è quello giusto?" |
| **IT (CTO)** | Sicurezza, manutenibilità | "Password in chiaro, SQL injection ovunque. Un audit ci boccia in 5 minuti." |
| **Management (CEO)** | Zero downtime durante modernizzazione | "Il portale non può fermarsi. Gli operatori lo usano 12 ore al giorno." |
| **Customer Service** | Visibilità stato per il cliente | "Vorremmo dare accesso ai clienti, ma il sistema non ha ruoli granulari." |

### Disaccordi espliciti

1. **Finance vs Operations**: Finance vuole bloccare la creazione ordini finché i totali non sono corretti. Operations dice "spediamo prima, sistemiamo dopo" perché i ritardi costano penali.
2. **IT vs Management**: IT vuole un freeze funzionale per mettere in sicurezza il sistema. Management rifiuta qualsiasi fermo.
3. **Warehouse vs Finance**: Warehouse usa GIACENZA, il vecchio report usa QTA_MAGAZZINO. Nessuno vuole migrare i propri flussi.
4. **Customer Service vs IT**: CS chiede un portale clienti esterno. IT dice che prima vanno sistemate autenticazione e autorizzazione.

---

## Epic 1: Gestione Ordini

### US-1.1: Visualizzazione lista ordini con filtri

**Come** operatore logistico  
**Voglio** vedere la lista degli ordini filtrata per cliente, stato e periodo  
**In modo da** trovare rapidamente gli ordini su cui devo agire

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | La lista mostra: numero ordine, cliente, data, consegna prevista, stato, importo | Aprire `/portal?action=orders` → verificare che tutte le colonne siano presenti |
| AC-2 | Il filtro per cliente cerca per ragione sociale (match parziale) | Inserire "Alpini" nel campo cliente → solo ordini di "Trasporti Alpini" visibili |
| AC-3 | Il filtro per stato mostra solo gli ordini in quello stato | Selezionare "Consegnato" → verificare che tutti i risultati abbiano stato "Consegnato" |
| AC-4 | Il filtro per data filtra su DATA_ORDINE nel range [da, a] | Inserire da=2024-02-01, a=2024-02-28 → solo ordini di febbraio 2024 |
| AC-5 | Senza filtri, tutti gli ordini sono visibili ordinati per data decrescente | Caricare la pagina senza parametri → ORD-2024-0009 è il primo |
| AC-6 | Gli stati non documentati (6, 7, 8) sono visualizzati con etichetta leggibile | Verificare che l'ordine in stato 7 mostri "Da Verificare" e non "7" |

**Priorità:** MUST — *Nessun disaccordo. Tutti gli stakeholder concordano.*

---

### US-1.2: Dettaglio ordine completo

**Come** operatore logistico  
**Voglio** vedere il dettaglio completo di un ordine (testata, righe, cliente, note)  
**In modo da** gestire l'ordine senza dover consultare altri sistemi

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Il dettaglio mostra: numero, data, consegna prevista/effettiva, stato, tracking | Aprire dettaglio ORD-2024-0003 → verificare tutti i campi |
| AC-2 | I dati cliente sono visibili: ragione sociale, P.IVA, indirizzo, città, email | Verificare sezione "Cliente" nel dettaglio |
| AC-3 | Le righe ordine mostrano: codice prodotto, descrizione, quantità, prezzo, sconto, importo | Verificare tabella righe con almeno 1 riga |
| AC-4 | Sono visibili sia il totale calcolato dalle righe sia il totale in testata | Verificare che entrambi i totali siano mostrati |
| AC-5 | Le note interne sono visibili | ORD-2024-0003 deve mostrare "Consegna in ritardo - traffico Brennero" |

**Priorità:** MUST

**⚠ Nota stakeholder (Finance):** AC-4 è stato aggiunto specificamente da Finance. Il fatto che i due totali possano differire è un bug noto. Finance vuole che la discrepanza sia **visibile**, non nascosta. Operations preferirebbe mostrare solo il totale in testata per non confondere gli operatori.

---

### US-1.3: Creazione nuovo ordine

**Come** operatore  
**Voglio** creare un nuovo ordine selezionando cliente e prodotti  
**In modo da** registrare le richieste dei clienti nel sistema

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Il form mostra la lista clienti attivi in un dropdown | Aprire `/portal?action=newOrder` → dropdown clienti popolato |
| AC-2 | I prodotti attivi sono disponibili per la selezione con prezzo visibile | Verificare lista prodotti con codice, descrizione, prezzo |
| AC-3 | L'ordine viene creato con stato "Bozza" (stato 0) | Creare ordine → verificare che lo stato sia "Bozza" |
| AC-4 | Il numero ordine segue il formato ORD-YYYY-NNNN | Creare ordine → numero deve essere ORD-2026-NNNN |
| AC-5 | La consegna prevista è calcolata automaticamente a +7 giorni | Creare ordine oggi → consegna prevista = oggi + 7 giorni |
| AC-6 | Lo sconto cliente (se presente) è applicato alle righe | Creare ordine per "Trasporti Alpini" (sconto 5%) → importo riga scontato |
| AC-7 | La giacenza del prodotto viene decrementata | Creare ordine con 3 unità di TRI-001 → GIACENZA decrementata di 3 |

**Priorità:** MUST

**⚠ Nota stakeholder (Finance):** AC-6 è ambiguo nel codice attuale. Lo sconto del cliente a volte viene applicato alla riga, a volte all'ordine, a volte a entrambi. Finance chiede una regola unica e documentata. **Decisione pendente.**

**⚠ Nota stakeholder (Warehouse):** AC-7 aggiorna solo il campo GIACENZA, non QTA_MAGAZZINO. Il vecchio report di magazzino usa QTA_MAGAZZINO. Warehouse chiede l'allineamento. **Decisione pendente.**

---

### US-1.4: Aggiornamento stato ordine

**Come** operatore logistico  
**Voglio** aggiornare lo stato di un ordine (Bozza → Confermato → In Lavorazione → Spedito → Consegnato)  
**In modo da** tracciare l'avanzamento della spedizione

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Il dropdown stato mostra tutte le opzioni valide | Dettaglio ordine → dropdown con: Bozza, Confermato, In Lavorazione, Spedito, Consegnato, Annullato |
| AC-2 | Il cambio stato viene registrato con utente e timestamp | Aggiornare stato → MODIFIED_BY e MODIFIED_DATE aggiornati |
| AC-3 | Quando lo stato passa a "Consegnato" (4), la data consegna effettiva viene impostata | Impostare stato "Consegnato" → DATA_CONSEGNA_EFFETTIVA = now |
| AC-4 | Lo stato può essere cambiato in qualsiasi direzione (nessuna validazione workflow) | Verificare che un ordine "Consegnato" possa tornare a "Bozza" |

**Priorità:** MUST

**⚠ Nota stakeholder (Operations):** AC-4 è un problema. Operations vuole una macchina a stati con transizioni obbligate (Bozza→Confermato→In Lavorazione→Spedito→Consegnato). Oggi chiunque può mettere qualsiasi stato, inclusi i misteriosi 6/7/8. Finance concorda: ordini "Annullati" che tornano "Confermati" creano discrepanze contabili. **Decisione pendente: definire la state machine.**

---

## Epic 2: Gestione Clienti

### US-2.1: Visualizzazione e ricerca clienti

**Come** operatore  
**Voglio** consultare la lista clienti e cercare per ragione sociale  
**In modo da** trovare i dati di un cliente quando ne ho bisogno

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | La lista mostra clienti attivi con: ragione sociale, P.IVA, città, sconto | Aprire `/portal?action=customers` → tabella clienti visibile |
| AC-2 | La ricerca filtra per ragione sociale (match parziale) | Cercare "Trasporti" → solo clienti con "Trasporti" nel nome |
| AC-3 | Clienti inattivi (FLAG_ATTIVO=0) non sono visibili | Verificare assenza clienti disattivati |

**Priorità:** SHOULD

**⚠ Bug noto:** La lista mostra clienti duplicati (es. "Trasporti Alpini S.r.l." e "Trasporti Alpini Srl" sono lo stesso cliente con due record). Nessuno stakeholder ha preso ownership della deduplicazione.

---

## Epic 3: Reportistica

### US-3.1: Report fatturato per cliente

**Come** manager  
**Voglio** vedere un report annuale del fatturato per cliente  
**In modo da** analizzare i ricavi e presentare i dati al board

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Il report mostra: cliente, numero ordini, totale, media per ordine | Aprire `/portal?action=report` → tabella con colonne corrette |
| AC-2 | Il report filtra per anno | Selezionare 2024 → solo ordini del 2024 |
| AC-3 | Gli ordini annullati (stato 5) sono esclusi dal conteggio | Verificare che ordini annullati non contribuiscano al totale |
| AC-4 | Il default è l'anno corrente | Aprire report senza parametri → anno = 2026 |

**Priorità:** SHOULD

**⚠ Nota stakeholder (Finance):** "I totali del report non tornano con quelli dell'ERP perché il campo IMPORTO_TOTALE in testata ordine non coincide con la somma delle righe. Il report usa IMPORTO_TOTALE. Il board fa domande." Finance chiede che il report calcoli il totale dalle righe, non dalla testata. Operations non vuole cambiare la logica per paura di rompere altri flussi.

---

## Epic 4: Autenticazione e Sicurezza

### US-4.1: Login sicuro

**Come** utente del portale  
**Voglio** autenticarmi con username e password  
**In modo da** accedere alle funzionalità del portale

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Login con credenziali valide (admin/admin123) reindirizza alla lista ordini | POST login → redirect a `/portal?action=orders` |
| AC-2 | Login con credenziali errate mostra messaggio di errore | POST login con password sbagliata → messaggio "Credenziali non valide" |
| AC-3 | Le pagine protette richiedono autenticazione | Accedere a `/portal?action=orders` senza sessione → redirect a login |
| AC-4 | Logout invalida la sessione | Click "Esci" → redirect a login, accesso diretto a `/portal` bloccato |

**Priorità:** MUST

**⚠ Debito tecnico critico (IT):**
- Password memorizzate in chiaro (no hash)
- SQL injection sul form di login (concatenazione stringhe)
- Nessun rate limiting sui tentativi di login
- Nessun CSRF token
- Ruoli (admin, operatore, magazzino, report) definiti come stringa libera, nessun controllo di autorizzazione

IT classifica questo come **rischio P0**. Management ha risposto: "Mettiamo in sicurezza, ma senza fermare il servizio."

---

## Epic 5: Integrità Dati (cross-cutting)

### US-5.1: Coerenza totali ordine

**Come** controller finanziario  
**Voglio** che il totale in testata ordine corrisponda alla somma delle righe  
**In modo da** produrre report affidabili per il board

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Per ogni ordine: IMPORTO_TOTALE = Σ(IMPORTO_RIGA) delle righe associate | Query: `SELECT o.ID FROM ORDINI o WHERE o.IMPORTO_TOTALE <> (SELECT SUM(r.IMPORTO_RIGA) FROM RIGHE_ORDINE r WHERE r.ID_ORDINE = o.ID)` → risultato vuoto |
| AC-2 | L'importo riga = quantità × prezzo unitario × (1 - sconto/100) | Per ogni riga, verificare la formula |

**Priorità:** MUST (Finance), COULD (Operations)

**⚠ Disaccordo aperto:** Finance vuole un batch di riallineamento immediato. Operations dice "non toccate i dati storici, i clienti hanno già le fatture". **Compromesso proposto:** riallineare solo gli ordini in stato Bozza/Confermato, congelare i totali degli ordini già Consegnati/Annullati.

---

### US-5.2: Unificazione campi giacenza

**Come** responsabile magazzino  
**Voglio** che esista un solo campo giacenza affidabile  
**In modo da** sapere quanta merce ho realmente in magazzino

**Acceptance Criteria:**

| # | Criterio | Verifica |
|---|---|---|
| AC-1 | Un solo campo giacenza è usato in tutto il sistema | Grep codebase: nessun riferimento a QTA_MAGAZZINO in codice applicativo |
| AC-2 | La giacenza viene decrementata alla creazione ordine | Creare ordine → verificare decremento |
| AC-3 | La giacenza viene incrementata all'annullamento ordine | Annullare ordine → verificare incremento |

**Priorità:** SHOULD (Warehouse), WON'T per ora (Operations — "il vecchio report di magazzino lo usa ancora")

---

## Riepilogo priorità (MoSCoW)

| ID | Story | MUST | SHOULD | COULD | WON'T |
|---|---|---|---|---|---|
| US-1.1 | Lista ordini con filtri | ✓ | | | |
| US-1.2 | Dettaglio ordine | ✓ | | | |
| US-1.3 | Creazione ordine | ✓ | | | |
| US-1.4 | Aggiornamento stato | ✓ | | | |
| US-2.1 | Clienti e ricerca | | ✓ | | |
| US-3.1 | Report per cliente | | ✓ | | |
| US-4.1 | Login sicuro | ✓ | | | |
| US-5.1 | Coerenza totali | ✓* | | | |
| US-5.2 | Unificazione giacenza | | ✓ | | |

*\* MUST per Finance, COULD per Operations — escalation al CEO pendente.*

---

## Decisioni pendenti

| # | Decisione | Owner | Deadline | Impatto |
|---|---|---|---|---|
| D-1 | Regola unica per applicazione sconto cliente (riga vs ordine vs entrambi) | Finance + Operations | Sprint 1 | US-1.3 AC-6 |
| D-2 | Definizione state machine ordini (transizioni valide tra stati) | Operations + Finance | Sprint 1 | US-1.4 AC-4 |
| D-3 | Allineamento o deprecazione QTA_MAGAZZINO | Warehouse + IT | Sprint 2 | US-5.2 |
| D-4 | Riallineamento totali ordini storici | Finance + Operations | Sprint 1 | US-5.1 |
| D-5 | Strategia sicurezza (hash password, prepared statements) durante servizio attivo | IT + Management | Sprint 1 | US-4.1 |
