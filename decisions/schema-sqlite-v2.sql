-- =============================================================
--  Brennero Logistics — Schema SQLite v2
--  Date: 2026-04-28
--  Changes from v1:
--   + clienti.classificazione  (gold/silver/bronze) — E2
--   + clienti.settore_merceologico                  — E2
--   + clienti.referente_commerciale                 — E2
--   + clienti.telefono_referente                    — E2
--   + prodotti.tipologia (TRASPORTO/DOGANA/...)      — E1
--   * utenti bootstrap data now uses named columns
-- =============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- UTENTI
-- -----------------------------------------------------------
CREATE TABLE utenti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT    NOT NULL UNIQUE,
    password_hash    TEXT    NOT NULL,
    nome_completo    TEXT,
    ruolo            TEXT    NOT NULL DEFAULT 'operatore'
                             CHECK (ruolo IN ('admin', 'operatore', 'magazzino', 'report')),
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    ultimo_accesso   TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- CLIENTI — v2 adds: classificazione, commercial fields
-- -----------------------------------------------------------
CREATE TABLE clienti (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    ragione_sociale         TEXT    NOT NULL,
    partita_iva             TEXT,
    codice_fiscale          TEXT,
    -- E2: customer classification (Gold=top tier, Bronze=standard)
    classificazione         TEXT    NOT NULL DEFAULT 'bronze'
                                    CHECK (classificazione IN ('gold', 'silver', 'bronze')),
    -- E2: billing
    pec                     TEXT,
    codice_sdi              TEXT,
    -- address
    indirizzo               TEXT,
    citta                   TEXT,
    cap                     TEXT,
    provincia               TEXT,
    paese                   TEXT    NOT NULL DEFAULT 'IT',
    -- contacts
    telefono                TEXT,
    email                   TEXT,
    -- E2: commercial fields
    settore_merceologico    TEXT,
    referente_commerciale   TEXT,
    telefono_referente      TEXT,
    -- commercial terms
    sconto_default          REAL    NOT NULL DEFAULT 0.0
                                    CHECK (sconto_default >= 0 AND sconto_default <= 100),
    attivo                  INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    note                    TEXT,
    created_at              TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- PRODOTTI — v2 adds: tipologia (E1 catalog types)
-- -----------------------------------------------------------
CREATE TABLE prodotti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codice           TEXT    NOT NULL UNIQUE,
    descrizione      TEXT,
    -- E1: product type — only MAGAZZINO has physical stock (giacenza)
    tipologia        TEXT    NOT NULL DEFAULT 'TRASPORTO'
                             CHECK (tipologia IN (
                                 'TRASPORTO',
                                 'DOGANA',
                                 'MAGAZZINO',
                                 'ASSICURAZIONE',
                                 'CONSULENZA'
                             )),
    prezzo_unitario  REAL    NOT NULL CHECK (prezzo_unitario >= 0),
    aliquota_iva     INTEGER NOT NULL DEFAULT 22
                             CHECK (aliquota_iva IN (0, 4, 5, 10, 22)),
    categoria        TEXT,
    -- only meaningful when tipologia = 'MAGAZZINO'; NULL for services
    giacenza         INTEGER DEFAULT NULL CHECK (giacenza IS NULL OR giacenza >= 0),
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1)),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- ORDINI
-- -----------------------------------------------------------
CREATE TABLE ordini (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ordine            TEXT    NOT NULL UNIQUE,
    id_cliente               INTEGER NOT NULL REFERENCES clienti(id),
    stato                    TEXT    NOT NULL DEFAULT 'bozza'
                                     CHECK (stato IN (
                                         'bozza',
                                         'confermato',
                                         'in_lavorazione',
                                         'spedito',
                                         'consegnato',
                                         'annullato'
                                     )),
    priorita                 TEXT    NOT NULL DEFAULT 'normale'
                                     CHECK (priorita IN ('bassa', 'normale', 'alta', 'urgente')),
    data_ordine              TEXT    NOT NULL DEFAULT (datetime('now')),
    data_consegna_prevista   TEXT,
    data_consegna_effettiva  TEXT,
    importo_lordo            REAL    NOT NULL DEFAULT 0.0,
    sconto_percentuale       REAL    NOT NULL DEFAULT 0.0
                                     CHECK (sconto_percentuale >= 0 AND sconto_percentuale <= 100),
    importo_netto            REAL    NOT NULL DEFAULT 0.0,
    tipo_spedizione          TEXT    DEFAULT 'standard'
                                     CHECK (tipo_spedizione IN (
                                         'standard', 'express', 'internazionale', 'ritiro_magazzino'
                                     )),
    peso_totale_kg           REAL    CHECK (peso_totale_kg IS NULL OR peso_totale_kg >= 0),
    volume_m3                REAL    CHECK (volume_m3 IS NULL OR volume_m3 >= 0),
    id_corriere              INTEGER,
    tracking                 TEXT,
    note_interne             TEXT,
    note_cliente             TEXT,
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
    importo_riga     REAL    NOT NULL,
    note             TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- ORDINI_ARCHIVIO — E5: archived orders (> 2 years, final state)
-- -----------------------------------------------------------
CREATE TABLE ordini_archivio (
    id                       INTEGER PRIMARY KEY,
    numero_ordine            TEXT    NOT NULL UNIQUE,
    id_cliente               INTEGER NOT NULL,
    stato                    TEXT    NOT NULL,
    priorita                 TEXT    NOT NULL,
    data_ordine              TEXT    NOT NULL,
    data_consegna_prevista   TEXT,
    data_consegna_effettiva  TEXT,
    importo_lordo            REAL    NOT NULL DEFAULT 0.0,
    sconto_percentuale       REAL    NOT NULL DEFAULT 0.0,
    importo_netto            REAL    NOT NULL DEFAULT 0.0,
    tipo_spedizione          TEXT,
    note_interne             TEXT,
    note_cliente             TEXT,
    created_by               TEXT,
    archived_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE righe_ordine_archivio (
    id               INTEGER PRIMARY KEY,
    id_ordine        INTEGER NOT NULL REFERENCES ordini_archivio(id) ON DELETE CASCADE,
    id_prodotto      INTEGER NOT NULL,
    quantita         INTEGER NOT NULL,
    prezzo_unitario  REAL    NOT NULL,
    sconto_riga      REAL    NOT NULL DEFAULT 0.0,
    importo_riga     REAL    NOT NULL,
    note             TEXT,
    created_at       TEXT
);

-- -----------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------
CREATE INDEX idx_ordini_cliente        ON ordini(id_cliente);
CREATE INDEX idx_ordini_stato          ON ordini(stato);
CREATE INDEX idx_ordini_priorita       ON ordini(priorita);
CREATE INDEX idx_righe_ordine          ON righe_ordine(id_ordine);
CREATE INDEX idx_clienti_piva          ON clienti(partita_iva);
CREATE INDEX idx_clienti_classe        ON clienti(classificazione);
CREATE INDEX idx_prodotti_tipologia    ON prodotti(tipologia);
CREATE INDEX idx_clienti_nome          ON clienti(ragione_sociale);

-- -----------------------------------------------------------
-- Migration script from v1 (for existing databases)
-- Run these ALTER TABLE statements if upgrading from v1:
--
--   ALTER TABLE clienti ADD COLUMN classificazione TEXT NOT NULL DEFAULT 'bronze'
--       CHECK (classificazione IN ('gold','silver','bronze'));
--   ALTER TABLE clienti ADD COLUMN settore_merceologico TEXT;
--   ALTER TABLE clienti ADD COLUMN referente_commerciale TEXT;
--   ALTER TABLE clienti ADD COLUMN telefono_referente TEXT;
--   ALTER TABLE prodotti ADD COLUMN tipologia TEXT NOT NULL DEFAULT 'TRASPORTO'
--       CHECK (tipologia IN ('TRASPORTO','DOGANA','MAGAZZINO','ASSICURAZIONE','CONSULENZA'));
--   UPDATE prodotti SET giacenza = NULL WHERE tipologia != 'MAGAZZINO';
-- -----------------------------------------------------------

-- -----------------------------------------------------------
-- Bootstrap data
-- -----------------------------------------------------------
INSERT INTO utenti (username, password_hash, nome_completo, ruolo) VALUES
    ('admin',       '$2b$12$PLACEHOLDER_HASH_admin',    'System Administrator',  'admin'),
    ('mrossi',      '$2b$12$PLACEHOLDER_HASH_mrossi',   'Mario Rossi',           'operatore'),
    ('lverdi',      '$2b$12$PLACEHOLDER_HASH_lverdi',   'Laura Verdi',           'operatore'),
    ('gbianchi',    '$2b$12$PLACEHOLDER_HASH_gbianchi', 'Giuseppe Bianchi',      'magazzino'),
    ('report_user', '$2b$12$PLACEHOLDER_HASH_report',   'Report User',           'report');

INSERT INTO clienti (ragione_sociale, partita_iva, classificazione, email, sconto_default) VALUES
    ('Trasporti Alpini S.r.l.',    '02345678901', 'gold',   'info@alpini.it',    5.0),
    ('Bresciani & Figli S.p.A.',   '03456789012', 'silver', 'info@bresciani.it', 3.0),
    ('Logistica Sud S.r.l.',       '04567890123', 'bronze', 'info@logsud.it',    0.0),
    ('Euro Trasporti S.r.l.',      '05678901234', 'silver', 'info@eurotrasporti.it', 2.5),
    ('Nord Express S.p.A.',        '06789012345', 'gold',   'info@nordexpress.it', 7.0);

INSERT INTO prodotti (codice, descrizione, tipologia, prezzo_unitario, aliquota_iva, giacenza) VALUES
    ('TRN-NAZ-001',  'National road transport',          'TRASPORTO',   450.00, 22, NULL),
    ('TRN-EU-001',   'EU international transport',       'TRASPORTO',   890.00, 22, NULL),
    ('TRN-EXP-001',  'Express delivery',                 'TRASPORTO',   650.00, 22, NULL),
    ('DOG-IMP-001',  'Import customs clearance',         'DOGANA',      320.00, 22, NULL),
    ('DOG-EXP-001',  'Export customs clearance',         'DOGANA',      280.00, 22, NULL),
    ('MAG-PAL-001',  'Pallet storage per month',         'MAGAZZINO',    45.00, 22, 500),
    ('MAG-PKG-001',  'Picking & packing',                'MAGAZZINO',    12.00, 22, 999),
    ('ASS-BASE-001', 'Basic cargo insurance',            'ASSICURAZIONE', 85.00, 22, NULL),
    ('ASS-ALL-001',  'All-risk cargo insurance',         'ASSICURAZIONE',150.00, 22, NULL),
    ('CON-LOG-001',  'Logistics consulting (day rate)',  'CONSULENZA',  950.00, 22, NULL),
    ('CON-AUD-001',  'Supply chain audit',               'CONSULENZA', 2800.00, 22, NULL);
