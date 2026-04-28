package com.brennero.portal;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * DatabaseManager - singleton per la connessione al database.
 * Creato nel 2015 da F. Trentini (non lavora piu' qui).
 * NON TOCCARE - se si rompe non abbiamo il numero di Trentini.
 */
public class DatabaseManager {

    private static DatabaseManager instance = null;
    private static Connection connection = null;

    // Connessione hardcodata - "tanto e' solo il DB locale"
    private static final String DB_URL = "jdbc:h2:mem:brennero;DB_CLOSE_DELAY=-1";
    private static final String DB_USER = "sa";
    private static final String DB_PASS = "";

    private DatabaseManager() {
        try {
            Class.forName("org.h2.Driver");
            connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            initDatabase();
        } catch (Exception e) {
            // Log? Che log? Stampiamo e basta
            System.out.println("ERRORE DATABASE: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static DatabaseManager getInstance() {
        if (instance == null) {
            instance = new DatabaseManager();
        }
        return instance;
    }

    public Connection getConnection() {
        try {
            if (connection == null || connection.isClosed()) {
                connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            }
        } catch (SQLException e) {
            System.out.println("ERRORE RICONNESSIONE: " + e.getMessage());
        }
        return connection;
    }

    private void initDatabase() {
        try {
            // Leggiamo schema e dati da file
            executeSqlFile("schema.sql");
            executeSqlFile("data.sql");
            System.out.println("Database inizializzato OK");
        } catch (Exception e) {
            System.out.println("ERRORE INIT DB: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void executeSqlFile(String filename) throws Exception {
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(
                getClass().getClassLoader().getResourceAsStream(filename)
            )
        );
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            // Ignora commenti
            if (line.trim().startsWith("--")) continue;
            sb.append(line);
            if (line.trim().endsWith(";")) {
                String sql = sb.toString().trim();
                if (!sql.isEmpty() && !sql.contains("CREATE TRIGGER")) {
                    Statement stmt = connection.createStatement();
                    stmt.execute(sql);
                    stmt.close();
                }
                sb = new StringBuilder();
            }
        }
        reader.close();
    }

    /**
     * Metodo di utilita' per query veloci.
     * Si', restituisce un ResultSet senza chiudere lo Statement.
     * No, non e' un buon pattern. Si', e' in produzione da 9 anni.
     */
    public ResultSet eseguiQuery(String sql) {
        try {
            Statement stmt = connection.createStatement();
            return stmt.executeQuery(sql);
        } catch (SQLException e) {
            System.out.println("ERRORE QUERY: " + sql);
            System.out.println(e.getMessage());
            return null;
        }
    }

    /**
     * Metodo di utilita' per INSERT/UPDATE/DELETE.
     */
    public int eseguiUpdate(String sql) {
        try {
            Statement stmt = connection.createStatement();
            int result = stmt.executeUpdate(sql);
            stmt.close();
            return result;
        } catch (SQLException e) {
            System.out.println("ERRORE UPDATE: " + sql);
            System.out.println(e.getMessage());
            return -1;
        }
    }

    // Metodo chiamato dal trigger (non funziona con H2 in-memory, ma e' nello schema)
    public static void ricalcolaTotale(Connection conn, Object[] args) throws SQLException {
        // In teoria ricalcola il totale dell'ordine sommando le righe.
        // In pratica non viene mai chiamato perche' il trigger e' commentato.
        // Il totale lo calcola OrderManager... a volte.
    }
}
