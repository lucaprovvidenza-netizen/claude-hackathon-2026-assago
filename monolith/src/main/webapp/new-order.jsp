<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.math.BigDecimal" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Nuovo Ordine</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <span class="logo">Brennero Logistics</span>
        <nav>
            <a href="portal?action=orders">Ordini</a>
            <a href="portal?action=customers">Clienti</a>
            <a href="portal?action=report">Report</a>
            <a href="portal?action=newOrder" class="btn btn-small active">+ Nuovo Ordine</a>
        </nav>
        <span class="user-info">
            <%= session.getAttribute("nomeCompleto") %>
            | <a href="portal?action=logout">Esci</a>
        </span>
    </div>

    <div class="content">
        <h2>Nuovo Ordine</h2>

        <% if (request.getParameter("errore") != null) { %>
            <div class="errore"><%= request.getParameter("errore") %></div>
        <% } %>

        <form method="POST" action="portal" id="formOrdine">
            <input type="hidden" name="action" value="saveOrder">

            <div class="form-section">
                <h3>Cliente</h3>
                <select name="idCliente" required class="form-control">
                    <option value="">-- Seleziona cliente --</option>
                    <%
                        List<Map<String, Object>> clienti = (List<Map<String, Object>>) request.getAttribute("clienti");
                        if (clienti != null) {
                            for (Map<String, Object> c : clienti) {
                    %>
                    <option value="<%= c.get("id") %>">
                        <%= c.get("ragioneSociale") %>
                        (<%= c.get("citta") %>)
                        <% if (((BigDecimal)c.get("scontoSpeciale")).doubleValue() > 0) { %>
                            - Sconto: <%= c.get("scontoSpeciale") %>%
                        <% } %>
                    </option>
                    <%
                            }
                        }
                    %>
                </select>
            </div>

            <div class="form-section">
                <h3>Prodotti</h3>
                <table class="tabella-dati" id="tabellaRighe">
                    <thead>
                        <tr>
                            <th>Prodotto</th>
                            <th>Prezzo Unit.</th>
                            <th>Qtà</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody id="righeOrdine">
                        <tr class="riga-ordine">
                            <td>
                                <select name="prodottoId" class="form-control" onchange="aggiornaPrezzo(this)">
                                    <option value="">-- Seleziona --</option>
                                    <%
                                        List<Map<String, Object>> prodotti = (List<Map<String, Object>>) request.getAttribute("prodotti");
                                        if (prodotti != null) {
                                            for (Map<String, Object> p : prodotti) {
                                    %>
                                    <option value="<%= p.get("id") %>"
                                            data-prezzo="<%= ((BigDecimal)p.get("prezzo")).doubleValue() %>">
                                        <%= p.get("codice") %> - <%= p.get("descrizione") %>
                                        (Disp: <%= p.get("giacenza") %>)
                                    </option>
                                    <%
                                            }
                                        }
                                    %>
                                </select>
                            </td>
                            <td class="prezzo-cell">-</td>
                            <td><input type="number" name="quantita" value="1" min="1" class="input-qty"></td>
                            <td><button type="button" onclick="rimuoviRiga(this)" class="btn btn-danger btn-small">X</button></td>
                        </tr>
                    </tbody>
                </table>
                <button type="button" onclick="aggiungiRiga()" class="btn btn-small">+ Aggiungi Riga</button>
            </div>

            <div class="form-section">
                <h3>Note</h3>
                <textarea name="noteCliente" rows="3" class="form-control"
                          placeholder="Note per il cliente..."></textarea>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Crea Ordine</button>
                <a href="portal?action=orders" class="btn">Annulla</a>
            </div>
        </form>
    </div>

    <!-- JavaScript inline, come nel 2015 -->
    <script>
        function aggiungiRiga() {
            var tbody = document.getElementById('righeOrdine');
            var prima = tbody.querySelector('.riga-ordine');
            var nuova = prima.cloneNode(true);
            nuova.querySelector('select').selectedIndex = 0;
            nuova.querySelector('.prezzo-cell').textContent = '-';
            nuova.querySelector('input[type="number"]').value = 1;
            tbody.appendChild(nuova);
        }

        function rimuoviRiga(btn) {
            var tbody = document.getElementById('righeOrdine');
            if (tbody.children.length > 1) {
                btn.closest('tr').remove();
            }
        }

        function aggiornaPrezzo(select) {
            var option = select.options[select.selectedIndex];
            var prezzo = option.getAttribute('data-prezzo');
            var cell = select.closest('tr').querySelector('.prezzo-cell');
            cell.textContent = prezzo ? ('€ ' + parseFloat(prezzo).toFixed(2)) : '-';
        }
    </script>

    <div class="footer">
        Brennero Logistics S.p.A. - Portale Ordini v1.0
    </div>
</body>
</html>
