package com.brennero.portal;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.sql.ResultSet;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * PortalServlet - LA servlet. Il God Object. Il cuore di tutto.
 * Gestisce TUTTE le azioni del portale tramite un parametro "action".
 * 
 * Mappa delle action (non esaustiva, alcune le ha aggiunte qualcuno a mano):
 *   login, logout, orders, orderDetail, newOrder, saveOrder,
 *   updateStatus, report, customers
 * 
 * Se non riconosci un'action, vai alla lista ordini. Almeno non da' 404.
 */
public class PortalServlet extends HttpServlet {

    private OrderManager orderManager;
    private CustomerManager customerManager;
    private DatabaseManager db;

    @Override
    public void init() throws ServletException {
        db = DatabaseManager.getInstance();
        orderManager = OrderManager.getInstance();
        customerManager = CustomerManager.getInstance();
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        processRequest(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        processRequest(req, resp);
    }

    /**
     * Unico metodo che gestisce tutto. GET e POST mischiati. Nessuna distinzione.
     */
    private void processRequest(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        req.setCharacterEncoding("UTF-8");
        resp.setCharacterEncoding("UTF-8");

        String action = req.getParameter("action");
        if (action == null) action = "orders";

        try {
            switch (action) {
                case "login":
                    doLogin(req, resp);
                    break;
                case "logout":
                    doLogout(req, resp);
                    break;
                case "orders":
                    doListaOrdini(req, resp);
                    break;
                case "orderDetail":
                    doDettaglioOrdine(req, resp);
                    break;
                case "newOrder":
                    doNuovoOrdine(req, resp);
                    break;
                case "saveOrder":
                    doSalvaOrdine(req, resp);
                    break;
                case "updateStatus":
                    doAggiornaStato(req, resp);
                    break;
                case "report":
                    doReport(req, resp);
                    break;
                case "customers":
                    doListaClienti(req, resp);
                    break;
                default:
                    // Action sconosciuta? Lista ordini. Almeno non esplode.
                    doListaOrdini(req, resp);
            }
        } catch (Exception e) {
            // Catch-all: stampa l'errore e redirect alla home
            System.out.println("ERRORE GENERICO: " + e.getMessage());
            e.printStackTrace();
            resp.sendRedirect(req.getContextPath() + "/portal?action=orders");
        }
    }

    private void doLogin(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String username = req.getParameter("username");
        String password = req.getParameter("password");

        if (username == null || password == null) {
            req.setAttribute("errore", "Inserire username e password");
            req.getRequestDispatcher("/login.jsp").forward(req, resp);
            return;
        }

        // Autenticazione: query diretta con credenziali concatenate
        String sql = "SELECT * FROM UTENTI WHERE USERNAME = '" + username
                   + "' AND PASSWORD = '" + password + "' AND FLAG_ATTIVO = 1";

        try {
            ResultSet rs = db.eseguiQuery(sql);
            if (rs != null && rs.next()) {
                HttpSession session = req.getSession(true);
                session.setAttribute("username", rs.getString("USERNAME"));
                session.setAttribute("nomeCompleto", rs.getString("NOME_COMPLETO"));
                session.setAttribute("ruolo", rs.getString("RUOLO"));

                // Aggiorna ultimo accesso
                String now = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
                db.eseguiUpdate("UPDATE UTENTI SET ULTIMO_ACCESSO = '" + now
                    + "' WHERE USERNAME = '" + username + "'");

                resp.sendRedirect(req.getContextPath() + "/portal?action=orders");
            } else {
                req.setAttribute("errore", "Credenziali non valide");
                req.getRequestDispatcher("/login.jsp").forward(req, resp);
            }
        } catch (Exception e) {
            req.setAttribute("errore", "Errore di sistema: " + e.getMessage());
            req.getRequestDispatcher("/login.jsp").forward(req, resp);
        }
    }

    private void doLogout(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        HttpSession session = req.getSession(false);
        if (session != null) {
            session.invalidate();
        }
        resp.sendRedirect(req.getContextPath() + "/login.jsp");
    }

    private void doListaOrdini(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String filtroCliente = req.getParameter("filtroCliente");
        String filtroStato = req.getParameter("filtroStato");
        String dataDa = req.getParameter("dataDa");
        String dataA = req.getParameter("dataA");

        List<Map<String, Object>> ordini = orderManager.cercaOrdini(
            filtroCliente, filtroStato, dataDa, dataA);

        req.setAttribute("ordini", ordini);
        req.setAttribute("filtroCliente", filtroCliente);
        req.setAttribute("filtroStato", filtroStato);
        req.setAttribute("dataDa", dataDa);
        req.setAttribute("dataA", dataA);

        req.getRequestDispatcher("/orders.jsp").forward(req, resp);
    }

    private void doDettaglioOrdine(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String idStr = req.getParameter("id");
        if (idStr == null) {
            resp.sendRedirect(req.getContextPath() + "/portal?action=orders");
            return;
        }

        int id = Integer.parseInt(idStr);
        Map<String, Object> ordine = orderManager.getOrdine(id);
        List<Map<String, Object>> righe = orderManager.getRigheOrdine(id);

        req.setAttribute("ordine", ordine);
        req.setAttribute("righe", righe);

        req.getRequestDispatcher("/order-detail.jsp").forward(req, resp);
    }

    private void doNuovoOrdine(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        List<Map<String, Object>> clienti = customerManager.getClientiAttivi();
        List<Map<String, Object>> prodotti = orderManager.getProdottiAttivi();

        req.setAttribute("clienti", clienti);
        req.setAttribute("prodotti", prodotti);

        req.getRequestDispatcher("/new-order.jsp").forward(req, resp);
    }

    private void doSalvaOrdine(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        int idCliente = Integer.parseInt(req.getParameter("idCliente"));
        String noteCliente = req.getParameter("noteCliente");
        String username = (String) req.getSession().getAttribute("username");

        // Parsing righe dal form - formato fragile
        String[] prodottiIds = req.getParameterValues("prodottoId");
        String[] quantita = req.getParameterValues("quantita");

        String[][] righe = null;
        if (prodottiIds != null) {
            righe = new String[prodottiIds.length][2];
            for (int i = 0; i < prodottiIds.length; i++) {
                righe[i][0] = prodottiIds[i];
                righe[i][1] = (quantita != null && i < quantita.length) ? quantita[i] : "1";
            }
        }

        int idOrdine = orderManager.creaOrdine(idCliente, noteCliente, righe, username);

        if (idOrdine > 0) {
            resp.sendRedirect(req.getContextPath()
                + "/portal?action=orderDetail&id=" + idOrdine);
        } else {
            resp.sendRedirect(req.getContextPath()
                + "/portal?action=newOrder&errore=Errore+creazione+ordine");
        }
    }

    private void doAggiornaStato(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        int idOrdine = Integer.parseInt(req.getParameter("idOrdine"));
        int nuovoStato = Integer.parseInt(req.getParameter("nuovoStato"));
        String username = (String) req.getSession().getAttribute("username");

        orderManager.aggiornaStato(idOrdine, nuovoStato, username);

        resp.sendRedirect(req.getContextPath()
            + "/portal?action=orderDetail&id=" + idOrdine);
    }

    private void doReport(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String anno = req.getParameter("anno");
        if (anno == null || anno.isEmpty()) {
            anno = new SimpleDateFormat("yyyy").format(new Date());
        }

        List<Map<String, Object>> report = orderManager.reportPerCliente(anno);

        req.setAttribute("report", report);
        req.setAttribute("anno", anno);

        req.getRequestDispatcher("/reports.jsp").forward(req, resp);
    }

    private void doListaClienti(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String termine = req.getParameter("termine");
        List<Map<String, Object>> clienti;

        if (termine != null && !termine.isEmpty()) {
            clienti = customerManager.cercaClienti(termine);
        } else {
            clienti = customerManager.getClientiAttivi();
        }

        req.setAttribute("clienti", clienti);
        req.setAttribute("termine", termine);

        req.getRequestDispatcher("/customers.jsp").forward(req, resp);
    }
}
