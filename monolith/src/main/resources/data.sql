-- Dati iniziali Brennero Logistics
-- Inseriti a mano nel 2016, mai puliti

INSERT INTO UTENTI (USERNAME, PASSWORD, NOME_COMPLETO, RUOLO) VALUES
('admin', 'admin123', 'Amministratore Sistema', 'admin'),
('mrossi', 'mario2016', 'Mario Rossi', 'operatore'),
('lverdi', 'password', 'Laura Verdi', 'operatore'),
('gbianchi', 'Gbianchi1!', 'Giuseppe Bianchi', 'magazzino'),
('report_user', 'report', 'Utente Report', 'report');

INSERT INTO CLIENTI (RAGIONE_SOCIALE, PARTITA_IVA, INDIRIZZO, CITTA, CAP, TELEFONO, EMAIL, SCONTO_SPECIALE, FLAG_ATTIVO) VALUES
('Trasporti Alpini S.r.l.', '01234567890', 'Via Roma 42', 'Bolzano', '39100', '+39 0471 555001', 'ordini@trasportialpini.it', 5.00, 1),
('LogiNord S.p.A.', '09876543210', 'Viale Europa 15', 'Trento', '38122', '+39 0461 555002', 'acquisti@loginord.com', 0, 1),
('Spedizioni Veloci di Conti G.', '11223344556', 'Via Brennero 88', 'Vipiteno', '39049', NULL, NULL, 10.00, 1),
('MegaStore Italia S.r.l.', '66778899001', 'Centro Direzionale Km 2', 'Milano', '20100', '+39 02 555003', 'procurement@megastore.it', 3.50, 1),
('CLIENTE CANCELLATO', '00000000000', '-', '-', '-', NULL, NULL, 0, 0),
('F.lli Marchetti & C.', '55443322110', 'Zona Industriale 7', 'Rovereto', '38068', '+39 0464 555004', 'info@marchetti.com', 0, 1),
-- cliente duplicato, nessuno ha il coraggio di cancellarlo
('Trasporti Alpini Srl', '01234567890', 'Via Roma, 42', 'BOLZANO', '39100', '0471555001', 'ordini@trasporti-alpini.it', 5.00, 1);

INSERT INTO PRODOTTI (CODICE, DESCRIZIONE, PREZZO_UNITARIO, IVA, CATEGORIA, GIACENZA, QTA_MAGAZZINO, FLAG_ATTIVO) VALUES
('TRN-001', 'Trasporto Standard Nazionale (per pallet)', 85.00, 22, 'trasporto', 999, 999, 1),
('TRN-002', 'Trasporto Express Nazionale (per pallet)', 145.00, 22, 'trasporto', 999, 999, 1),
('TRI-001', 'Trasporto Internazionale EU (per pallet)', 220.00, 22, 'trasporto', 999, 999, 1),
('MAG-001', 'Stoccaggio Magazzino (per pallet/mese)', 35.00, 22, 'magazzino', 500, 480, 1),
('MAG-002', 'Picking & Packing (per collo)', 4.50, 22, 'magazzino', 999, 999, 1),
('ASS-001', 'Assicurazione Merce (per spedizione)', 25.00, 10, 'assicurazione', 999, 999, 1),
('DOG-001', 'Pratica Doganale', 180.00, 22, 'dogana', 999, 999, 1),
-- prodotto fantasma, il codice e' sbagliato ma ha ordini collegati
('TRN001', 'Trasporto Standard', 80.00, 22, 'trasporto', 0, 0, 0);

INSERT INTO ORDINI (NUMERO_ORDINE, ID_CLIENTE, DATA_ORDINE, DATA_CONSEGNA_PREVISTA, DATA_CONSEGNA_EFFETTIVA, STATO, IMPORTO_TOTALE, SCONTO_PERCENTUALE, NOTE_INTERNE, CREATED_BY) VALUES
('ORD-2024-0001', 1, '2024-01-15 09:30:00', '2024-01-22 00:00:00', '2024-01-21 14:00:00', 4, 595.00, 5.00, NULL, 'mrossi'),
('ORD-2024-0002', 2, '2024-01-18 11:00:00', '2024-01-25 00:00:00', NULL, 5, 0, 0, 'Annullato dal cliente', 'mrossi'),
('ORD-2024-0003', 1, '2024-02-01 08:45:00', '2024-02-08 00:00:00', '2024-02-10 16:30:00', 4, 1250.00, 5.00, 'Consegna in ritardo - traffico Brennero', 'lverdi'),
('ORD-2024-0004', 3, '2024-02-10 14:20:00', '2024-02-17 00:00:00', '2024-02-15 09:00:00', 4, 890.00, 10.00, NULL, 'mrossi'),
('ORD-2024-0005', 4, '2024-03-01 10:00:00', '2024-03-08 00:00:00', NULL, 2, 3200.00, 3.50, 'In attesa conferma magazzino', 'lverdi'),
('ORD-2024-0006', 1, '2024-03-05 16:00:00', '2024-03-12 00:00:00', NULL, 1, 425.50, 5.00, NULL, 'mrossi'),
('ORD-2024-0007', 6, '2024-03-10 09:15:00', NULL, NULL, 0, NULL, 0, 'Bozza - cliente deve confermare', 'mrossi'),
-- ordine con stato misterioso 7
('ORD-2024-0008', 3, '2024-03-15 11:30:00', '2024-03-22 00:00:00', NULL, 7, 660.00, 10.00, 'Stato settato manualmente da DB', 'admin'),
-- ordine collegato al cliente duplicato
('ORD-2024-0009', 7, '2024-03-20 08:00:00', '2024-03-27 00:00:00', NULL, 1, 170.00, 5.00, NULL, 'lverdi');

INSERT INTO RIGHE_ORDINE (ID_ORDINE, ID_PRODOTTO, QUANTITA, PREZZO_UNITARIO, SCONTO_RIGA, IMPORTO_RIGA) VALUES
(1, 1, 5, 85.00, 0, 425.00),
(1, 6, 5, 25.00, 0, 125.00),
(1, 5, 10, 4.50, 0, 45.00),
(3, 3, 4, 220.00, 0, 880.00),
(3, 7, 2, 180.00, 0, 360.00),
-- nota: importo_riga non corrisponde a quantita * prezzo - sconto
(3, 5, 5, 4.50, 0, 10.00),
(4, 2, 5, 145.00, 0, 725.00),
(4, 6, 5, 25.00, 0, 125.00),
(4, 5, 10, 4.50, 10.00, 40.50),
(5, 3, 10, 220.00, 0, 2200.00),
(5, 4, 20, 35.00, 0, 700.00),
(5, 5, 50, 4.50, 5.00, 213.75),
-- riga con prodotto fantasma
(5, 8, 1, 80.00, 0, 80.00),
(6, 1, 5, 85.00, 5.00, 403.75),
(6, 6, 1, 25.00, 0, 25.00),
(9, 1, 2, 85.00, 5.00, 161.50),
(9, 5, 2, 4.50, 0, 9.00);
