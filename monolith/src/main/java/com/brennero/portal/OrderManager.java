package com.brennero.portal;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * OrderManager - gestisce TUTTO degli ordini.
 * Logica di business, accesso al DB, calcoli, validazione, formattazione.
 * 
 * Autore originale: F. Trentini (2015)
 * Modificato da: mezzo ufficio (2016-2024)
 * 
 * TODO (dal 2018): spezzare questa classe
 */
public class OrderManager {

    private DatabaseManager db;
    // Riferimento circolare con CustomerManager
    private CustomerManager customerManager;

    // Singleton anche questo, perche' no
    private static OrderManager instance;

    private OrderManager() {
        db = DatabaseManager.getInstance();
        // customerManager viene settato dopo per evitare loop infinito nel costruttore
    }

    public static OrderManager getInstance() {
        if (instance == null) {
            instance = new OrderManager();
            instance.customerManager = CustomerManager.getInstance();
        }
        return instance;
    }

    /**
     * Cerca ordini. SQL costruito con concatenazione di stringhe.
     * "Tanto i parametri vengono dai nostri form" - F. Trentini, 2015
     */
    public List<Map<String, Object>> cercaOrdini(String filtroCliente, String filtroStato,
                                                   String dataDa, String dataA) {
        List<Map<String, Object>> risultati = new ArrayList<>();

        // Query costruita dinamicamente con concatenazione
        String sql = "SELECT o.*, c.RAGIONE_SOCIALE FROM ORDINI o "
                   + "LEFT JOIN CLIENTI c ON o.ID_CLIENTE = c.ID WHERE 1=1";

        if (filtroCliente != null && !filtroCliente.isEmpty()) {
            sql += " AND c.RAGIONE_SOCIALE LIKE '%" + filtroCliente + "%'";
        }
        if (filtroStato != null && !filtroStato.isEmpty()) {
            sql += " AND o.STATO = " + filtroStato;
        }
        if (dataDa != null && !dataDa.isEmpty()) {
            sql += " AND o.DATA_ORDINE >= '" + dataDa + "'";
        }
        if (dataA != null && !dataA.isEmpty()) {
            sql += " AND o.DATA_ORDINE <= '" + dataA + " 23:59:59'";
        }

        sql += " ORDER BY o.DATA_ORDINE DESC";

        try {
            ResultSet rs = db.eseguiQuery(sql);
            while (rs != null && rs.next()) {
                Map<String, Object> ordine = new HashMap<>();
                ordine.put("id", rs.getInt("ID"));
                ordine.put("numeroOrdine", rs.getString("NUMERO_ORDINE"));
                ordine.put("cliente", rs.getString("RAGIONE_SOCIALE"));
                ordine.put("idCliente", rs.getInt("ID_CLIENTE"));
                ordine.put("dataOrdine", rs.getTimestamp("DATA_ORDINE"));
                ordine.put("dataConsegnaPrevista", rs.getTimestamp("DATA_CONSEGNA_PREVISTA"));
                ordine.put("dataConsegnaEffettiva", rs.getTimestamp("DATA_CONSEGNA_EFFETTIVA"));
                ordine.put("stato", rs.getInt("STATO"));
                ordine.put("statoDescrizione", getDescrizioneStato(rs.getInt("STATO")));
                ordine.put("importoTotale", rs.getBigDecimal("IMPORTO_TOTALE"));
                ordine.put("sconto", rs.getBigDecimal("SCONTO_PERCENTUALE"));
                ordine.put("noteInterne", rs.getString("NOTE_INTERNE"));
                risultati.add(ordine);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE cercaOrdini: " + e.getMessage());
        }

        return risultati;
    }

    public Map<String, Object> getOrdine(int id) {
        String sql = "SELECT o.*, c.RAGIONE_SOCIALE, c.PARTITA_IVA, c.INDIRIZZO, c.CITTA, c.EMAIL "
                   + "FROM ORDINI o LEFT JOIN CLIENTI c ON o.ID_CLIENTE = c.ID "
                   + "WHERE o.ID = " + id;
        try {
            ResultSet rs = db.eseguiQuery(sql);
            if (rs != null && rs.next()) {
                Map<String, Object> ordine = new HashMap<>();
                ordine.put("id", rs.getInt("ID"));
                ordine.put("numeroOrdine", rs.getString("NUMERO_ORDINE"));
                ordine.put("cliente", rs.getString("RAGIONE_SOCIALE"));
                ordine.put("idCliente", rs.getInt("ID_CLIENTE"));
                ordine.put("piva", rs.getString("PARTITA_IVA"));
                ordine.put("indirizzo", rs.getString("INDIRIZZO"));
                ordine.put("citta", rs.getString("CITTA"));
                ordine.put("emailCliente", rs.getString("EMAIL"));
                ordine.put("dataOrdine", rs.getTimestamp("DATA_ORDINE"));
                ordine.put("dataConsegnaPrevista", rs.getTimestamp("DATA_CONSEGNA_PREVISTA"));
                ordine.put("dataConsegnaEffettiva", rs.getTimestamp("DATA_CONSEGNA_EFFETTIVA"));
                ordine.put("stato", rs.getInt("STATO"));
                ordine.put("statoDescrizione", getDescrizioneStato(rs.getInt("STATO")));
                ordine.put("importoTotale", rs.getBigDecimal("IMPORTO_TOTALE"));
                ordine.put("sconto", rs.getBigDecimal("SCONTO_PERCENTUALE"));
                ordine.put("noteInterne", rs.getString("NOTE_INTERNE"));
                ordine.put("noteCliente", rs.getString("NOTE_CLIENTE"));
                ordine.put("tracking", rs.getString("TRACKING"));
                return ordine;
            }
        } catch (SQLException e) {
            System.out.println("ERRORE getOrdine: " + e.getMessage());
        }
        return null;
    }

    public List<Map<String, Object>> getRigheOrdine(int idOrdine) {
        List<Map<String, Object>> righe = new ArrayList<>();
        String sql = "SELECT r.*, p.CODICE, p.DESCRIZIONE as DESC_PRODOTTO "
                   + "FROM RIGHE_ORDINE r LEFT JOIN PRODOTTI p ON r.ID_PRODOTTO = p.ID "
                   + "WHERE r.ID_ORDINE = " + idOrdine;
        try {
            ResultSet rs = db.eseguiQuery(sql);
            while (rs != null && rs.next()) {
                Map<String, Object> riga = new HashMap<>();
                riga.put("id", rs.getInt("ID"));
                riga.put("codiceProdotto", rs.getString("CODICE"));
                riga.put("descrizione", rs.getString("DESC_PRODOTTO"));
                riga.put("quantita", rs.getInt("QUANTITA"));
                riga.put("prezzoUnitario", rs.getBigDecimal("PREZZO_UNITARIO"));
                riga.put("scontoRiga", rs.getBigDecimal("SCONTO_RIGA"));
                riga.put("importoRiga", rs.getBigDecimal("IMPORTO_RIGA"));
                righe.add(riga);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE getRigheOrdine: " + e.getMessage());
        }
        return righe;
    }

    /**
     * Crea un nuovo ordine. Genera il numero ordine, inserisce le righe,
     * calcola il totale (a modo suo), e aggiorna la giacenza.
     * Tutto in un metodo. Nessuna transazione.
     */
    public int creaOrdine(int idCliente, String noteCliente, String[][] righe, String username) {
        // Genera numero ordine: ORD-YYYY-NNNN
        String anno = new SimpleDateFormat("yyyy").format(new Date());
        String sql = "SELECT MAX(ID) as MAX_ID FROM ORDINI";
        int nextId = 1;
        try {
            ResultSet rs = db.eseguiQuery(sql);
            if (rs != null && rs.next()) {
                nextId = rs.getInt("MAX_ID") + 1;
            }
        } catch (SQLException e) {
            // Se fallisce, usiamo 9999. Cosa potrebbe andare storto?
            nextId = 9999;
        }
        String numeroOrdine = "ORD-" + anno + "-" + String.format("%04d", nextId);

        // Prendi lo sconto del cliente
        double scontoCliente = 0;
        try {
            Map<String, Object> cliente = customerManager.getCliente(idCliente);
            if (cliente != null && cliente.get("scontoSpeciale") != null) {
                scontoCliente = ((Number) cliente.get("scontoSpeciale")).doubleValue();
            }
        } catch (Exception e) {
            // Se non riesce a leggere lo sconto, va avanti senza
        }

        // Timestamp formattato a mano
        String now = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        String consegnaPrevista = new SimpleDateFormat("yyyy-MM-dd").format(
            new Date(System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000)
        ) + " 00:00:00";

        // INSERT ordine
        String insertOrdine = "INSERT INTO ORDINI (NUMERO_ORDINE, ID_CLIENTE, DATA_ORDINE, "
            + "DATA_CONSEGNA_PREVISTA, STATO, IMPORTO_TOTALE, SCONTO_PERCENTUALE, "
            + "NOTE_CLIENTE, CREATED_BY, MODIFIED_BY, MODIFIED_DATE) VALUES ('"
            + numeroOrdine + "', " + idCliente + ", '" + now + "', '"
            + consegnaPrevista + "', 0, 0, " + scontoCliente + ", '"
            + (noteCliente != null ? noteCliente.replace("'", "''") : "")
            + "', '" + username + "', '" + username + "', '" + now + "')";

        db.eseguiUpdate(insertOrdine);

        // Recupera ID dell'ordine appena inserito (race condition? quale race condition?)
        int idOrdine = -1;
        try {
            ResultSet rs = db.eseguiQuery(
                "SELECT ID FROM ORDINI WHERE NUMERO_ORDINE = '" + numeroOrdine + "'");
            if (rs != null && rs.next()) {
                idOrdine = rs.getInt("ID");
            }
        } catch (SQLException e) {
            System.out.println("ERRORE recupero ID ordine: " + e.getMessage());
            return -1;
        }

        // Inserisci righe e calcola totale
        double totale = 0;
        if (righe != null) {
            for (String[] riga : righe) {
                if (riga == null || riga.length < 2) continue;
                int idProdotto = Integer.parseInt(riga[0]);
                int quantita = Integer.parseInt(riga[1]);

                // Prendi prezzo dal prodotto
                double prezzo = 0;
                try {
                    ResultSet rs = db.eseguiQuery(
                        "SELECT PREZZO_UNITARIO FROM PRODOTTI WHERE ID = " + idProdotto);
                    if (rs != null && rs.next()) {
                        prezzo = rs.getDouble("PREZZO_UNITARIO");
                    }
                } catch (SQLException e) {
                    // Prezzo 0? Prezzo 0.
                }

                double importoRiga = quantita * prezzo;
                // Lo sconto del cliente si applica alla riga? All'ordine? A entrambi?
                // Risposta: dipende da chi ha scritto il codice quel giorno
                double scontoRiga = 0;
                if (scontoCliente > 0) {
                    scontoRiga = scontoCliente;
                    importoRiga = importoRiga * (1 - scontoCliente / 100);
                }

                String insertRiga = "INSERT INTO RIGHE_ORDINE (ID_ORDINE, ID_PRODOTTO, QUANTITA, "
                    + "PREZZO_UNITARIO, SCONTO_RIGA, IMPORTO_RIGA) VALUES ("
                    + idOrdine + ", " + idProdotto + ", " + quantita + ", "
                    + prezzo + ", " + scontoRiga + ", " + importoRiga + ")";
                db.eseguiUpdate(insertRiga);

                totale += importoRiga;

                // Aggiorna giacenza (solo GIACENZA, non QTA_MAGAZZINO, perche'?)
                db.eseguiUpdate("UPDATE PRODOTTI SET GIACENZA = GIACENZA - " + quantita
                    + " WHERE ID = " + idProdotto);
            }
        }

        // Aggiorna totale ordine
        db.eseguiUpdate("UPDATE ORDINI SET IMPORTO_TOTALE = " + totale
            + " WHERE ID = " + idOrdine);

        return idOrdine;
    }

    public boolean aggiornaStato(int idOrdine, int nuovoStato, String username) {
        String now = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        String sql = "UPDATE ORDINI SET STATO = " + nuovoStato
                   + ", MODIFIED_BY = '" + username + "'"
                   + ", MODIFIED_DATE = '" + now + "'";

        // Se consegnato, segna la data
        if (nuovoStato == 4) {
            sql += ", DATA_CONSEGNA_EFFETTIVA = '" + now + "'";
        }

        sql += " WHERE ID = " + idOrdine;
        return db.eseguiUpdate(sql) > 0;
    }

    /**
     * Report totale ordini per cliente. Usato dal management.
     * Non e' propriamente compito di OrderManager, ma qui siamo.
     */
    public List<Map<String, Object>> reportPerCliente(String anno) {
        List<Map<String, Object>> report = new ArrayList<>();
        String sql = "SELECT c.RAGIONE_SOCIALE, COUNT(o.ID) as NUM_ORDINI, "
                   + "SUM(o.IMPORTO_TOTALE) as TOTALE, "
                   + "AVG(o.IMPORTO_TOTALE) as MEDIA "
                   + "FROM ORDINI o JOIN CLIENTI c ON o.ID_CLIENTE = c.ID "
                   + "WHERE YEAR(o.DATA_ORDINE) = " + anno + " "
                   + "AND o.STATO <> 5 "
                   + "GROUP BY c.RAGIONE_SOCIALE ORDER BY TOTALE DESC";
        try {
            ResultSet rs = db.eseguiQuery(sql);
            while (rs != null && rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("cliente", rs.getString("RAGIONE_SOCIALE"));
                row.put("numOrdini", rs.getInt("NUM_ORDINI"));
                row.put("totale", rs.getBigDecimal("TOTALE"));
                row.put("media", rs.getBigDecimal("MEDIA"));
                report.add(row);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE report: " + e.getMessage());
        }
        return report;
    }

    // Mappatura stati - hardcodata, ovviamente
    public static String getDescrizioneStato(int stato) {
        switch (stato) {
            case 0: return "Bozza";
            case 1: return "Confermato";
            case 2: return "In Lavorazione";
            case 3: return "Spedito";
            case 4: return "Consegnato";
            case 5: return "Annullato";
            // Stati non documentati ma presenti nei dati
            case 6: return "Sospeso";
            case 7: return "Da Verificare";
            case 8: return "Errore";
            default: return "Sconosciuto (" + stato + ")";
        }
    }

    public List<Map<String, Object>> getProdottiAttivi() {
        List<Map<String, Object>> prodotti = new ArrayList<>();
        try {
            ResultSet rs = db.eseguiQuery(
                "SELECT * FROM PRODOTTI WHERE FLAG_ATTIVO = 1 ORDER BY CODICE");
            while (rs != null && rs.next()) {
                Map<String, Object> p = new HashMap<>();
                p.put("id", rs.getInt("ID"));
                p.put("codice", rs.getString("CODICE"));
                p.put("descrizione", rs.getString("DESCRIZIONE"));
                p.put("prezzo", rs.getBigDecimal("PREZZO_UNITARIO"));
                p.put("giacenza", rs.getInt("GIACENZA"));
                prodotti.add(p);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE getProdottiAttivi: " + e.getMessage());
        }
        return prodotti;
    }
}
