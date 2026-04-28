-- =============================================================
--  Brennero Logistics — Schema SQLite v1 (modernizzato)
--  Generato: 2026-04-28
--  Differenze rispetto al monolith H2:
--   • Tipi SQLite nativi (TEXT, INTEGER, REAL, NUMERIC)
--   • FK abilitate (PRAGMA foreign_keys = ON nell'app)
--   • Campi E2: priorità ordine, PEC, SDI, peso, volume, tipo spedizione
--   • Status ordine come TEXT enum, non INT libero
--   • Password hashata (bcrypt) — no più plaintext
--   • Rimosso QTA_MAGAZZINO (duplicato di GIACENZA)
--   • Alembic gestisce le migrazioni (questo file è la baseline)
-- =============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- UTENTI
-- -----------------------------------------------------------
CREATE TABLE utenti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT    NOT NULL UNIQUE,
    password_hash    TEXT    NOT NULL,                         -- bcrypt, mai plaintext
    nome_completo    TEXT,
    ruolo            TEXT    NOT NULL DEFAULT 'operatore'
                             CHECK (ruolo IN ('admin', 'operatore', 'magazzino', 'report')),
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    ultimo_accesso   TEXT,                                     -- ISO-8601
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- CLIENTI  (+ campi E2: PEC, codice_sdi per fatturazione)
-- -----------------------------------------------------------
CREATE TABLE clienti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ragione_sociale  TEXT    NOT NULL,
    partita_iva      TEXT,
    codice_fiscale   TEXT,
    -- E2: campi fatturazione elettronica italiana
    pec              TEXT,
    codice_sdi       TEXT,
    -- indirizzo
    indirizzo        TEXT,
    citta            TEXT,
    cap              TEXT,
    provincia        TEXT,
    paese            TEXT    NOT NULL DEFAULT 'IT',
    -- contatti
    telefono         TEXT,
    email            TEXT,
    -- commerciale
    sconto_default   REAL    NOT NULL DEFAULT 0.0
                             CHECK (sconto_default >= 0 AND sconto_default <= 100),
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    note             TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- PRODOTTI  (rimosso qta_magazzino duplicato)
-- -----------------------------------------------------------
CREATE TABLE prodotti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codice           TEXT    NOT NULL UNIQUE,
    descrizione      TEXT,
    prezzo_unitario  REAL    NOT NULL CHECK (prezzo_unitario >= 0),
    aliquota_iva     INTEGER NOT NULL DEFAULT 22
                             CHECK (aliquota_iva IN (0, 4, 5, 10, 22)),
    categoria        TEXT,
    giacenza         INTEGER NOT NULL DEFAULT 0 CHECK (giacenza >= 0),
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- ORDINI  (+ campi E2: priorità, tipo_spedizione, peso, volume)
-- -----------------------------------------------------------
CREATE TABLE ordini (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ordine            TEXT    NOT NULL UNIQUE,
    id_cliente               INTEGER NOT NULL REFERENCES clienti(id),

    -- stato come enum testuale — nessun intero misterioso
    stato                    TEXT    NOT NULL DEFAULT 'bozza'
                                     CHECK (stato IN (
                                         'bozza',
                                         'confermato',
                                         'in_lavorazione',
                                         'spedito',
                                         'consegnato',
                                         'annullato'
                                     )),

    -- E2: priorità
    priorita                 TEXT    NOT NULL DEFAULT 'normale'
                                     CHECK (priorita IN ('bassa', 'normale', 'alta', 'urgente')),

    -- date
    data_ordine              TEXT    NOT NULL DEFAULT (datetime('now')),
    data_consegna_prevista   TEXT,
    data_consegna_effettiva  TEXT,

    -- importi
    importo_lordo            REAL    NOT NULL DEFAULT 0.0,
    sconto_percentuale       REAL    NOT NULL DEFAULT 0.0
                                     CHECK (sconto_percentuale >= 0 AND sconto_percentuale <= 100),
    importo_netto            REAL    NOT NULL DEFAULT 0.0,   -- calcolato dall'app, non da trigger

    -- E2: logistica estesa
    tipo_spedizione          TEXT    DEFAULT 'standard'
                                     CHECK (tipo_spedizione IN (
                                         'standard', 'express', 'internazionale', 'ritiro_magazzino'
                                     )),
    peso_totale_kg           REAL    CHECK (peso_totale_kg IS NULL OR peso_totale_kg >= 0),
    volume_m3                REAL    CHECK (volume_m3 IS NULL OR volume_m3 >= 0),

    -- corriere / tracking (presenti nel monolith ma mai completati — ora tipizzati)
    id_corriere              INTEGER,
    tracking                 TEXT,

    -- note
    note_interne             TEXT,
    note_cliente             TEXT,

    -- audit
    created_by               TEXT,
    updated_by               TEXT,
    created_at               TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at               TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- RIGHE_ORDINE
-- -----------------------------------------------------------
CREATE TABLE righe_ordine (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ordine        INTEGER NOT NULL REFERENCES ordini(id) ON DELETE CASCADE,
    id_prodotto      INTEGER NOT NULL REFERENCES prodotti(id),
    quantita         INTEGER NOT NULL CHECK (quantita > 0),
    prezzo_unitario  REAL    NOT NULL CHECK (prezzo_unitario >= 0),
    sconto_riga      REAL    NOT NULL DEFAULT 0.0
                             CHECK (sconto_riga >= 0 AND sconto_riga <= 100),
    importo_riga     REAL    NOT NULL,                        -- calcolato dall'app
    note             TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- Indici
-- -----------------------------------------------------------
CREATE INDEX idx_ordini_cliente    ON ordini(id_cliente);
CREATE INDEX idx_ordini_stato      ON ordini(stato);
CREATE INDEX idx_ordini_priorita   ON ordini(priorita);
CREATE INDEX idx_righe_ordine      ON righe_ordine(id_ordine);
CREATE INDEX idx_clienti_piva      ON clienti(partita_iva);

-- -----------------------------------------------------------
-- Dati di bootstrap (password hashed con bcrypt in produzione;
-- qui placeholder da sostituire in fase di seed)
-- -----------------------------------------------------------
INSERT INTO utenti (username, password_hash, nome_completo, ruolo) VALUES
    ('admin',       '$2b$12$PLACEHOLDER_HASH_admin',    'Amministratore Sistema', 'admin'),
    ('mrossi',      '$2b$12$PLACEHOLDER_HASH_mrossi',   'Mario Rossi',            'operatore'),
    ('lverdi',      '$2b$12$PLACEHOLDER_HASH_lverdi',   'Laura Verdi',            'operatore'),
    ('gbianchi',    '$2b$12$PLACEHOLDER_HASH_gbianchi', 'Giuseppe Bianchi',       'magazzino'),
    ('report_user', '$2b$12$PLACEHOLDER_HASH_report',   'Utente Report',          'report');
