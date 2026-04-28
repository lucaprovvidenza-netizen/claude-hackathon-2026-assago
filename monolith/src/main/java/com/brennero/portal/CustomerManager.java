package com.brennero.portal;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * CustomerManager - gestisce i clienti.
 * Dipendenza circolare con OrderManager per "comodita'".
 */
public class CustomerManager {

    private DatabaseManager db;
    // Riferimento circolare: CustomerManager -> OrderManager -> CustomerManager
    private OrderManager orderManager;

    private static CustomerManager instance;

    private CustomerManager() {
        db = DatabaseManager.getInstance();
    }

    public static CustomerManager getInstance() {
        if (instance == null) {
            instance = new CustomerManager();
            instance.orderManager = OrderManager.getInstance();
        }
        return instance;
    }

    public Map<String, Object> getCliente(int id) {
        String sql = "SELECT * FROM CLIENTI WHERE ID = " + id;
        try {
            ResultSet rs = db.eseguiQuery(sql);
            if (rs != null && rs.next()) {
                Map<String, Object> cliente = new HashMap<>();
                cliente.put("id", rs.getInt("ID"));
                cliente.put("ragioneSociale", rs.getString("RAGIONE_SOCIALE"));
                cliente.put("partitaIva", rs.getString("PARTITA_IVA"));
                cliente.put("indirizzo", rs.getString("INDIRIZZO"));
                cliente.put("citta", rs.getString("CITTA"));
                cliente.put("cap", rs.getString("CAP"));
                cliente.put("telefono", rs.getString("TELEFONO"));
                cliente.put("email", rs.getString("EMAIL"));
                cliente.put("scontoSpeciale", rs.getBigDecimal("SCONTO_SPECIALE"));
                cliente.put("attivo", rs.getInt("FLAG_ATTIVO") == 1);
                return cliente;
            }
        } catch (SQLException e) {
            System.out.println("ERRORE getCliente: " + e.getMessage());
        }
        return null;
    }

    public List<Map<String, Object>> getClientiAttivi() {
        List<Map<String, Object>> clienti = new ArrayList<>();
        // NOTA: include il duplicato, nessuno ha scritto una DISTINCT
        String sql = "SELECT * FROM CLIENTI WHERE FLAG_ATTIVO = 1 ORDER BY RAGIONE_SOCIALE";
        try {
            ResultSet rs = db.eseguiQuery(sql);
            while (rs != null && rs.next()) {
                Map<String, Object> c = new HashMap<>();
                c.put("id", rs.getInt("ID"));
                c.put("ragioneSociale", rs.getString("RAGIONE_SOCIALE"));
                c.put("partitaIva", rs.getString("PARTITA_IVA"));
                c.put("citta", rs.getString("CITTA"));
                c.put("scontoSpeciale", rs.getBigDecimal("SCONTO_SPECIALE"));
                clienti.add(c);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE getClientiAttivi: " + e.getMessage());
        }
        return clienti;
    }

    /**
     * Cerca clienti per nome. SQL injection? Mai sentita.
     */
    public List<Map<String, Object>> cercaClienti(String termine) {
        List<Map<String, Object>> clienti = new ArrayList<>();
        String sql = "SELECT * FROM CLIENTI WHERE RAGIONE_SOCIALE LIKE '%" + termine + "%'"
                   + " AND FLAG_ATTIVO = 1";
        try {
            ResultSet rs = db.eseguiQuery(sql);
            while (rs != null && rs.next()) {
                Map<String, Object> c = new HashMap<>();
                c.put("id", rs.getInt("ID"));
                c.put("ragioneSociale", rs.getString("RAGIONE_SOCIALE"));
                c.put("partitaIva", rs.getString("PARTITA_IVA"));
                c.put("citta", rs.getString("CITTA"));
                clienti.add(c);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE cercaClienti: " + e.getMessage());
        }
        return clienti;
    }

    /**
     * Numero totale ordini del cliente - business logic che non c'entra niente qui
     */
    public int contaOrdiniCliente(int idCliente) {
        String sql = "SELECT COUNT(*) as CNT FROM ORDINI WHERE ID_CLIENTE = " + idCliente
                   + " AND STATO <> 5";
        try {
            ResultSet rs = db.eseguiQuery(sql);
            if (rs != null && rs.next()) {
                return rs.getInt("CNT");
            }
        } catch (SQLException e) {
            System.out.println("ERRORE contaOrdini: " + e.getMessage());
        }
        return 0;
    }
}
