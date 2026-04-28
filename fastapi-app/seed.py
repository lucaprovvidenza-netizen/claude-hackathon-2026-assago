"""Inizializza il database: crea le tabelle via Alembic e carica i dati di seed."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import bcrypt as _bcrypt
from sqlalchemy import create_engine, text

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH  = os.getenv("DB_PATH", str(BASE_DIR / "brennero.db"))
engine   = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def _hash(pw: str) -> str:
    return _bcrypt.hashpw(pw.encode(), _bcrypt.gensalt()).decode()


SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS utenti (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    nome_completo   TEXT,
    ruolo           TEXT    NOT NULL DEFAULT 'operatore'
                            CHECK (ruolo IN ('admin','operatore','magazzino','report')),
    attivo          INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0,1)),
    ultimo_accesso  TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS clienti (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    ragione_sociale          TEXT    NOT NULL,
    partita_iva              TEXT,
    codice_fiscale           TEXT,
    pec                      TEXT,
    codice_sdi               TEXT,
    indirizzo                TEXT,
    citta                    TEXT,
    cap                      TEXT,
    provincia                TEXT,
    paese                    TEXT    NOT NULL DEFAULT 'IT',
    telefono                 TEXT,
    email                    TEXT,
    -- E2 commercial fields (US-2.1 AC-2)
    settore_merceologico     TEXT,
    referente_commerciale    TEXT,
    telefono_referente       TEXT,
    sconto_default           REAL    NOT NULL DEFAULT 0.0,
    -- E2: classificazione Gold/Silver/Bronze
    classificazione          TEXT    NOT NULL DEFAULT 'silver'
                                     CHECK (classificazione IN ('gold','silver','bronze')),
    attivo                   INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0,1)),
    note                     TEXT,
    created_at               TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at               TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS prodotti (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codice           TEXT    NOT NULL UNIQUE,
    descrizione      TEXT,
    prezzo_unitario  REAL    NOT NULL DEFAULT 0.0,
    aliquota_iva     INTEGER NOT NULL DEFAULT 22
                             CHECK (aliquota_iva IN (0,4,5,10,22)),
    categoria        TEXT,
    -- E1: tipologia prodotto (5 categorie)
    tipologia        TEXT    NOT NULL DEFAULT 'TRASPORTO'
                             CHECK (tipologia IN (
                                 'TRASPORTO','DOGANA','MAGAZZINO',
                                 'ASSICURAZIONE','CONSULENZA'
                             )),
    giacenza         INTEGER DEFAULT NULL,
    attivo           INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0,1)),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ordini (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ordine            TEXT    NOT NULL UNIQUE,
    id_cliente               INTEGER NOT NULL REFERENCES clienti(id),
    stato                    TEXT    NOT NULL DEFAULT 'bozza'
                                     CHECK (stato IN (
                                         'bozza','confermato','in_lavorazione',
                                         'spedito','consegnato','annullato'
                                     )),
    priorita                 TEXT    NOT NULL DEFAULT 'normale'
                                     CHECK (priorita IN ('bassa','normale','alta','urgente')),
    data_ordine              TEXT    NOT NULL DEFAULT (datetime('now')),
    data_consegna_prevista   TEXT,
    data_consegna_effettiva  TEXT,
    importo_lordo            REAL    NOT NULL DEFAULT 0.0,
    sconto_percentuale       REAL    NOT NULL DEFAULT 0.0,
    importo_netto            REAL    NOT NULL DEFAULT 0.0,
    tipo_spedizione          TEXT    DEFAULT 'standard'
                                     CHECK (tipo_spedizione IN (
                                         'standard','express','internazionale','ritiro_magazzino'
                                     )),
    peso_totale_kg           REAL,
    volume_m3                REAL,
    id_corriere              INTEGER,
    tracking                 TEXT,
    note_interne             TEXT,
    note_cliente             TEXT,
    created_by               TEXT,
    updated_by               TEXT,
    created_at               TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at               TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS righe_ordine (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ordine        INTEGER NOT NULL REFERENCES ordini(id) ON DELETE CASCADE,
    id_prodotto      INTEGER NOT NULL REFERENCES prodotti(id),
    quantita         INTEGER NOT NULL CHECK (quantita > 0),
    prezzo_unitario  REAL    NOT NULL,
    sconto_riga      REAL    NOT NULL DEFAULT 0.0,
    importo_riga     REAL    NOT NULL,
    note             TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ordini_archivio (
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

CREATE TABLE IF NOT EXISTS righe_ordine_archivio (
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

CREATE INDEX IF NOT EXISTS idx_ordini_cliente   ON ordini(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ordini_stato     ON ordini(stato);
CREATE INDEX IF NOT EXISTS idx_ordini_priorita  ON ordini(priorita);
CREATE INDEX IF NOT EXISTS idx_righe_ordine     ON righe_ordine(id_ordine);
CREATE INDEX IF NOT EXISTS idx_clienti_piva     ON clienti(partita_iva);
CREATE INDEX IF NOT EXISTS idx_archivio_cliente ON ordini_archivio(id_cliente);
"""

# mapping stato INT monolite → TEXT enum
STATO_MAP = {0:"bozza",1:"confermato",2:"in_lavorazione",
             3:"spedito",4:"consegnato",5:"annullato"}


def init_db():
    with engine.begin() as conn:
        managed_by_alembic = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        )).fetchone()
        if managed_by_alembic:
            print("Schema gestito da Alembic — skip CREATE, eseguo solo seed.")
        else:
            for stmt in SCHEMA.split(";"):
                s = stmt.strip()
                if s:
                    conn.execute(text(s))
            _upgrade_clienti_v2(conn)

    _seed()
    print("Database inizializzato.")


def _upgrade_clienti_v2(conn):
    """Add E2 columns to an existing v1 clienti table; ignore duplicates."""
    columns = [
        ("codice_fiscale",        "TEXT"),
        ("pec",                   "TEXT"),
        ("codice_sdi",            "TEXT"),
        ("cap",                   "TEXT"),
        ("provincia",             "TEXT"),
        ("paese",                 "TEXT NOT NULL DEFAULT 'IT'"),
        ("settore_merceologico",  "TEXT"),
        ("referente_commerciale", "TEXT"),
        ("telefono_referente",    "TEXT"),
        ("classificazione",       "TEXT NOT NULL DEFAULT 'silver'"),
        ("note",                  "TEXT"),
    ]
    for col, ddl in columns:
        try:
            conn.execute(text(f"ALTER TABLE clienti ADD COLUMN {col} {ddl}"))
        except Exception:
            # SQLite raises on duplicate column; safe to ignore
            pass


def _seed():
    users = [
        ("admin",       "admin123",  "Amministratore Sistema", "admin"),
        ("mrossi",      "mario2016", "Mario Rossi",            "operatore"),
        ("lverdi",      "password",  "Laura Verdi",            "operatore"),
        ("gbianchi",    "Gbianchi1!","Giuseppe Bianchi",       "magazzino"),
        ("report_user", "report",    "Utente Report",          "report"),
    ]
    # (rs, p_iva, indirizzo, citta, telefono, email, sconto, classif,
    #  cap, provincia, pec, codice_sdi, settore, referente, tel_ref)
    clienti = [
        ("Trasporti Alpini S.r.l.",       "01234567890", "Via Roma 42",              "Bolzano",  "+39 0471 555001", "ordini@trasportialpini.it",   5.0,  "gold",
         "39100", "BZ", "trasportialpini@pec.it",  "M5UXCR1", "Trasporti su gomma",  "Marco Bianchi",   "+39 348 1234567"),
        ("LogiNord S.p.A.",               "09876543210", "Viale Europa 15",          "Trento",   "+39 0461 555002", "acquisti@loginord.com",       0.0,  "silver",
         "38122", "TN", "loginord@pec.it",         "USAL8PV", "Logistica integrata", "Anna Rossi",      "+39 335 9876543"),
        ("Spedizioni Veloci di Conti G.", "11223344556", "Via Brennero 88",          "Vipiteno", None,              None,                          10.0, "silver",
         "39049", "BZ", None,                      None,      "Corriere espresso",   "Giuseppe Conti",  None),
        ("MegaStore Italia S.r.l.",       "66778899001", "Centro Direzionale Km 2",  "Milano",   "+39 02 555003",   "procurement@megastore.it",    3.5,  "gold",
         "20100", "MI", "megastore@pec.it",        "T04ZHR3", "Retail GDO",          "Laura Verdi",     "+39 320 1112233"),
        ("F.lli Marchetti & C.",          "55443322110", "Zona Industriale 7",       "Rovereto", "+39 0464 555004", "info@marchetti.com",          0.0,  "bronze",
         "38068", "TN", None,                      None,      "Manifatturiero",      "Paolo Marchetti", "+39 348 5556677"),
        # legacy duplicate — preserved for characterization test
        ("Trasporti Alpini Srl",          "01234567890", "Via Roma, 42",             "Bolzano",  "0471555001",      "ordini@trasporti-alpini.it",  5.0,  "gold",
         "39100", "BZ", None,                      None,      "Trasporti su gomma",  "Marco Bianchi",   None),
    ]
    prodotti = [
        ("TRN-001", "Trasporto Standard Nazionale (per pallet)",  85.0,  22, "TRASPORTO",   None),
        ("TRN-002", "Trasporto Express Nazionale (per pallet)",   145.0, 22, "TRASPORTO",   None),
        ("TRI-001", "Trasporto Internazionale EU (per pallet)",   220.0, 22, "TRASPORTO",   None),
        ("TRI-002", "Trasporto Internazionale Extra-EU (pallet)", 310.0, 22, "TRASPORTO",   None),
        ("TRN-003", "Groupage Nazionale (per collo)",              28.0, 22, "TRASPORTO",   None),
        ("TRN-004", "Full Truck Load (FTL)",                     950.0, 22, "TRASPORTO",   None),
        ("DOG-001", "Pratica Doganale Import",                   180.0, 22, "DOGANA",      None),
        ("DOG-002", "Pratica Doganale Export",                   160.0, 22, "DOGANA",      None),
        ("DOG-003", "Sdoganamento Magazzino Doganale",           220.0, 22, "DOGANA",      None),
        ("MAG-001", "Stoccaggio Magazzino (per pallet/mese)",     35.0, 22, "MAGAZZINO",   500),
        ("MAG-002", "Picking & Packing (per collo)",               4.5, 22, "MAGAZZINO",   999),
        ("MAG-003", "Etichettatura (per collo)",                   2.0, 22, "MAGAZZINO",   999),
        ("ASS-001", "Assicurazione Merce Base (per spedizione)",  25.0, 10, "ASSICURAZIONE",None),
        ("ASS-002", "All-Risk Cargo (per spedizione)",            55.0, 10, "ASSICURAZIONE",None),
        ("CON-001", "Consulenza Logistica (ora)",                120.0, 22, "CONSULENZA",  None),
        ("CON-002", "Audit Supply Chain (giornata)",             850.0, 22, "CONSULENZA",  None),
    ]
    ordini = [
        # (numero, id_cliente, stato_int, priorita, data_ordine, data_cons_prev, data_cons_eff, importo_lordo, sconto_pct, note_int, created_by)
        ("ORD-2024-0001",1,4,"normale","2024-01-15 09:30:00","2024-01-22","2024-01-21", 595.0,  5.0, None,                             "mrossi"),
        ("ORD-2024-0002",2,5,"bassa", "2024-01-18 11:00:00","2024-01-25",None,           0.0,  0.0, "Annullato dal cliente",           "mrossi"),
        ("ORD-2024-0003",1,4,"normale","2024-02-01 08:45:00","2024-02-08","2024-02-10",1250.0,  5.0, "Consegna in ritardo - Brennero",  "lverdi"),
        ("ORD-2024-0004",3,4,"alta",  "2024-02-10 14:20:00","2024-02-17","2024-02-15", 890.0, 10.0, None,                             "mrossi"),
        ("ORD-2024-0005",4,2,"urgente","2024-03-01 10:00:00","2024-03-08",None,         3200.0,  3.5, "In attesa conferma magazzino",   "lverdi"),
        ("ORD-2024-0006",1,1,"normale","2024-03-05 16:00:00","2024-03-12",None,          425.5,  5.0, None,                            "mrossi"),
        ("ORD-2024-0007",5,0,"bassa", "2024-03-10 09:15:00",None,        None,           None,  0.0, "Bozza - cliente da confermare",  "mrossi"),
        ("ORD-2024-0008",6,1,"normale","2024-03-20 08:00:00","2024-03-27",None,          170.0,  5.0, None,                            "lverdi"),
    ]
    righe = [
        (1,1, 5, 85.0,  0,   425.0),
        (1,13,5, 25.0,  0,   125.0),
        (1,11,10, 4.5,  0,    45.0),
        (3,3, 4,220.0,  0,   880.0),
        (3,7, 2,180.0,  0,   360.0),
        (3,11,5,  4.5,  0,    22.5),
        (4,2, 5,145.0,  0,   725.0),
        (4,13,5, 25.0,  0,   125.0),
        (5,3,10,220.0,  0,  2200.0),
        (5,10,20,35.0,  0,   700.0),
        (5,11,50, 4.5, 5.0,  213.75),
        (6,1, 5, 85.0,  5.0, 403.75),
        (6,13,1, 25.0,  0,    25.0),
        (8,1, 2, 85.0,  5.0, 161.5),
        (8,11,2,  4.5,  0,     9.0),
    ]

    with engine.begin() as conn:
        for u in users:
            h = _hash(u[1])
            conn.execute(text(
                "INSERT OR IGNORE INTO utenti (username,password_hash,nome_completo,ruolo) "
                "VALUES (:u,:h,:n,:r)"
            ), {"u": u[0], "h": h, "n": u[2], "r": u[3]})

        for i, c in enumerate(clienti, 1):
            conn.execute(text(
                "INSERT OR IGNORE INTO clienti "
                "(id,ragione_sociale,partita_iva,indirizzo,citta,telefono,email,"
                " sconto_default,classificazione,cap,provincia,pec,codice_sdi,"
                " settore_merceologico,referente_commerciale,telefono_referente) "
                "VALUES (:id,:rs,:pi,:ind,:ci,:tel,:em,"
                " :sc,:cl,:cap,:prov,:pec,:sdi,"
                " :sett,:ref,:tref)"
            ), {"id":i,"rs":c[0],"pi":c[1],"ind":c[2],"ci":c[3],
                "tel":c[4],"em":c[5],"sc":c[6],"cl":c[7],
                "cap":c[8],"prov":c[9],"pec":c[10],"sdi":c[11],
                "sett":c[12],"ref":c[13],"tref":c[14]})

        for i, p in enumerate(prodotti, 1):
            conn.execute(text(
                "INSERT OR IGNORE INTO prodotti "
                "(id,codice,descrizione,prezzo_unitario,aliquota_iva,tipologia,giacenza) "
                "VALUES (:id,:co,:de,:pr,:iv,:ti,:gi)"
            ), {"id":i,"co":p[0],"de":p[1],"pr":p[2],"iv":p[3],
                "ti":p[4],"gi":p[5]})

        for i, o in enumerate(ordini, 1):
            # tuple: (numero,id_cliente,stato_int,priorita,data_ord,data_cp,data_ce,importo,sconto,note,created_by)
            stato = STATO_MAP.get(o[2], "bozza")
            netto = round((o[7] or 0) * (1 - (o[8] or 0) / 100), 2)
            conn.execute(text(
                "INSERT OR IGNORE INTO ordini "
                "(id,numero_ordine,id_cliente,stato,priorita,data_ordine,"
                "data_consegna_prevista,data_consegna_effettiva,"
                "importo_lordo,sconto_percentuale,importo_netto,"
                "note_interne,created_by) "
                "VALUES (:id,:no,:ic,:st,:pr,:do,:dcp,:dce,"
                ":il,:sp,:in_,:ni,:cb)"
            ), {"id":i,"no":o[0],"ic":o[1],"st":stato,"pr":o[3],
                "do":o[4],"dcp":o[5],"dce":o[6],
                "il":o[7] or 0,"sp":o[8],"in_":netto,
                "ni":o[9],"cb":o[10]})

        for r in righe:
            conn.execute(text(
                "INSERT OR IGNORE INTO righe_ordine "
                "(id_ordine,id_prodotto,quantita,prezzo_unitario,sconto_riga,importo_riga) "
                "VALUES (:io,:ip,:q,:pu,:sr,:ir)"
            ), {"io":r[0],"ip":r[1],"q":r[2],"pu":r[3],"sr":r[4],"ir":r[5]})


if __name__ == "__main__":
    init_db()
