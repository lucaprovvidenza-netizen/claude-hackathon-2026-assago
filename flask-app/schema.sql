-- Schema Brennero Logistics — porta SQLite da H2
-- Modifiche rispetto al monolite:
--   - AUTO_INCREMENT → INTEGER PRIMARY KEY AUTOINCREMENT
--   - Trigger H2-specifico rimosso (logica spostata in Python)
--   - E2: aggiunto PRIORITA su CLIENTI (1=Alta 2=Media 3=Bassa)
--   - E1: aggiunto TIPO su PRODOTTI ('Servizio'|'Materiale')

CREATE TABLE IF NOT EXISTS CLIENTI (
    ID               INTEGER PRIMARY KEY AUTOINCREMENT,
    RAGIONE_SOCIALE  TEXT    NOT NULL,
    PARTITA_IVA      TEXT,
    INDIRIZZO        TEXT,
    CITTA            TEXT,
    CAP              TEXT,
    TELEFONO         TEXT,
    EMAIL            TEXT,
    SCONTO_SPECIALE  REAL    DEFAULT 0,
    FLAG_ATTIVO      INTEGER DEFAULT 1,
    -- E2: priorità cliente (1=Alta, 2=Media, 3=Bassa)
    PRIORITA         INTEGER DEFAULT 2,
    NOTE             TEXT,
    DATA_INSERIMENTO TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS PRODOTTI (
    ID              INTEGER PRIMARY KEY AUTOINCREMENT,
    CODICE          TEXT    NOT NULL,
    DESCRIZIONE     TEXT,
    PREZZO_UNITARIO REAL,
    IVA             INTEGER DEFAULT 22,
    CATEGORIA       TEXT,
    -- E1: tipo prodotto/servizio
    TIPO            TEXT    DEFAULT 'Servizio',
    GIACENZA        INTEGER DEFAULT 0,
    QTA_MAGAZZINO   INTEGER DEFAULT 0,
    FLAG_ATTIVO     INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ORDINI (
    ID                      INTEGER PRIMARY KEY AUTOINCREMENT,
    NUMERO_ORDINE           TEXT,
    ID_CLIENTE              INTEGER,
    DATA_ORDINE             TEXT,
    DATA_CONSEGNA_PREVISTA  TEXT,
    DATA_CONSEGNA_EFFETTIVA TEXT,
    -- stati: 0=bozza 1=confermato 2=in lavorazione 3=spedito 4=consegnato 5=annullato
    STATO                   INTEGER DEFAULT 0,
    IMPORTO_TOTALE          REAL,
    SCONTO_PERCENTUALE      REAL    DEFAULT 0,
    NOTE_INTERNE            TEXT,
    NOTE_CLIENTE            TEXT,
    ID_CORRIERE             INTEGER DEFAULT NULL,
    TRACKING                TEXT    DEFAULT NULL,
    CREATED_BY              TEXT,
    MODIFIED_BY             TEXT,
    MODIFIED_DATE           TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS RIGHE_ORDINE (
    ID              INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_ORDINE       INTEGER,
    ID_PRODOTTO     INTEGER,
    QUANTITA        INTEGER,
    PREZZO_UNITARIO REAL,
    SCONTO_RIGA     REAL    DEFAULT 0,
    IMPORTO_RIGA    REAL,
    NOTE            TEXT
);

CREATE TABLE IF NOT EXISTS UTENTI (
    ID            INTEGER PRIMARY KEY AUTOINCREMENT,
    USERNAME      TEXT    NOT NULL,
    -- password in chiaro, come nel monolite — da non toccare per mantenere parità comportamentale
    PASSWORD      TEXT    NOT NULL,
    NOME_COMPLETO TEXT,
    RUOLO         TEXT    DEFAULT 'operatore',
    FLAG_ATTIVO   INTEGER DEFAULT 1,
    ULTIMO_ACCESSO TEXT
);
