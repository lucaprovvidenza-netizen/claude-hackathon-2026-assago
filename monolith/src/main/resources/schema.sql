-- Schema Brennero Logistics - Portale Ordini
-- NOTA: tutto in un unico file, nessuna migrazione, come da tradizione

CREATE TABLE IF NOT EXISTS CLIENTI (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    RAGIONE_SOCIALE VARCHAR(255) NOT NULL,
    PARTITA_IVA VARCHAR(20),
    INDIRIZZO VARCHAR(500),
    CITTA VARCHAR(100),
    CAP VARCHAR(10),
    TELEFONO VARCHAR(50),
    EMAIL VARCHAR(255),
    -- campo aggiunto nel 2019 da qualcuno, mai documentato
    SCONTO_SPECIALE DECIMAL(5,2) DEFAULT 0,
    -- flag misterioso, nessuno sa cosa fa ma se lo togli si rompe tutto
    FLAG_ATTIVO INT DEFAULT 1,
    NOTE TEXT,
    DATA_INSERIMENTO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PRODOTTI (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CODICE VARCHAR(50) NOT NULL,
    DESCRIZIONE VARCHAR(500),
    PREZZO_UNITARIO DECIMAL(10,2),
    -- IVA hardcodata, a volte 22 a volte 10, dipende da chi ha inserito il record
    IVA INT DEFAULT 22,
    CATEGORIA VARCHAR(100),
    GIACENZA INT DEFAULT 0,
    -- campo duplicato con GIACENZA, usato dal vecchio report
    QTA_MAGAZZINO INT DEFAULT 0,
    FLAG_ATTIVO INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ORDINI (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NUMERO_ORDINE VARCHAR(50),
    ID_CLIENTE INT,
    DATA_ORDINE TIMESTAMP,
    DATA_CONSEGNA_PREVISTA TIMESTAMP,
    DATA_CONSEGNA_EFFETTIVA TIMESTAMP,
    -- stati: 0=bozza, 1=confermato, 2=in lavorazione, 3=spedito, 4=consegnato, 5=annullato
    -- ma qualcuno ha usato anche 6, 7, 8 senza documentare
    STATO INT DEFAULT 0,
    IMPORTO_TOTALE DECIMAL(12,2),
    -- sconto calcolato a volte qui, a volte nella riga, a volte in entrambi
    SCONTO_PERCENTUALE DECIMAL(5,2) DEFAULT 0,
    NOTE_INTERNE TEXT,
    NOTE_CLIENTE TEXT,
    -- aggiunto per un progetto nel 2020, mai completato
    ID_CORRIERE INT DEFAULT NULL,
    TRACKING VARCHAR(255) DEFAULT NULL,
    CREATED_BY VARCHAR(100),
    MODIFIED_BY VARCHAR(100),
    MODIFIED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS RIGHE_ORDINE (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    ID_ORDINE INT,
    ID_PRODOTTO INT,
    QUANTITA INT,
    PREZZO_UNITARIO DECIMAL(10,2),
    -- a volte diverso dal prezzo in PRODOTTI, nessuna FK, nessun trigger
    SCONTO_RIGA DECIMAL(5,2) DEFAULT 0,
    IMPORTO_RIGA DECIMAL(12,2),
    NOTE VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS UTENTI (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    USERNAME VARCHAR(100) NOT NULL,
    -- password in chiaro, come da tradizione 2015
    PASSWORD VARCHAR(100) NOT NULL,
    NOME_COMPLETO VARCHAR(255),
    -- ruoli: admin, operatore, magazzino, report - stringa libera
    RUOLO VARCHAR(50) DEFAULT 'operatore',
    FLAG_ATTIVO INT DEFAULT 1,
    ULTIMO_ACCESSO TIMESTAMP
);

-- Trigger che calcola il totale ordine - la business logic vive qui
CREATE TRIGGER IF NOT EXISTS TRG_CALCOLA_TOTALE
AFTER INSERT ON RIGHE_ORDINE
FOR EACH ROW
CALL "com.brennero.portal.DatabaseManager.ricalcolaTotale";
