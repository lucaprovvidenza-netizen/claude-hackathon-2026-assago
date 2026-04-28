<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.text.SimpleDateFormat, java.math.BigDecimal" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Ordini</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <span class="logo">Brennero Logistics</span>
        <nav>
            <a href="portal?action=orders" class="active">Ordini</a>
            <a href="portal?action=customers">Clienti</a>
            <a href="portal?action=report">Report</a>
            <a href="portal?action=newOrder" class="btn btn-small">+ Nuovo Ordine</a>
        </nav>
        <span class="user-info">
            <%= session.getAttribute("nomeCompleto") %>
            (<%= session.getAttribute("ruolo") %>)
            | <a href="portal?action=logout">Esci</a>
        </span>
    </div>

    <div class="content">
        <h2>Lista Ordini</h2>

        <!-- Filtri inline, nessun JS, tutto server-side -->
        <form method="GET" action="portal" class="filtri-form">
            <input type="hidden" name="action" value="orders">
            <label>Cliente:
                <input type="text" name="filtroCliente"
                       value="<%= request.getAttribute("filtroCliente") != null ? request.getAttribute("filtroCliente") : "" %>">
            </label>
            <label>Stato:
                <select name="filtroStato">
                    <option value="">Tutti</option>
                    <option value="0" <%= "0".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>Bozza</option>
                    <option value="1" <%= "1".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>Confermato</option>
                    <option value="2" <%= "2".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>In Lavorazione</option>
                    <option value="3" <%= "3".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>Spedito</option>
                    <option value="4" <%= "4".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>Consegnato</option>
                    <option value="5" <%= "5".equals(request.getAttribute("filtroStato")) ? "selected" : "" %>>Annullato</option>
                </select>
            </label>
            <label>Da:
                <input type="date" name="dataDa"
                       value="<%= request.getAttribute("dataDa") != null ? request.getAttribute("dataDa") : "" %>">
            </label>
            <label>A:
                <input type="date" name="dataA"
                       value="<%= request.getAttribute("dataA") != null ? request.getAttribute("dataA") : "" %>">
            </label>
            <button type="submit" class="btn">Filtra</button>
        </form>

        <table class="tabella-dati">
            <thead>
                <tr>
                    <th>N. Ordine</th>
                    <th>Cliente</th>
                    <th>Data</th>
                    <th>Consegna Prevista</th>
                    <th>Stato</th>
                    <th>Importo</th>
                    <th>Azioni</th>
                </tr>
            </thead>
            <tbody>
                <%
                    List<Map<String, Object>> ordini = (List<Map<String, Object>>) request.getAttribute("ordini");
                    SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy");
                    if (ordini != null) {
                        for (Map<String, Object> o : ordini) {
                %>
                <tr>
                    <td><%= o.get("numeroOrdine") %></td>
                    <td><%= o.get("cliente") != null ? o.get("cliente") : "N/D" %></td>
                    <td><%= o.get("dataOrdine") != null ? sdf.format(o.get("dataOrdine")) : "-" %></td>
                    <td><%= o.get("dataConsegnaPrevista") != null ? sdf.format(o.get("dataConsegnaPrevista")) : "-" %></td>
                    <td>
                        <span class="stato stato-<%= o.get("stato") %>">
                            <%= o.get("statoDescrizione") %>
                        </span>
                    </td>
                    <td class="importo">
                        <%
                            BigDecimal importo = (BigDecimal) o.get("importoTotale");
                            out.print(importo != null ? String.format("€ %,.2f", importo) : "-");
                        %>
                    </td>
                    <td>
                        <a href="portal?action=orderDetail&id=<%= o.get("id") %>"
                           class="btn btn-small">Dettaglio</a>
                    </td>
                </tr>
                <%
                        }
                    }
                    if (ordini == null || ordini.isEmpty()) {
                %>
                <tr><td colspan="7" class="vuoto">Nessun ordine trovato</td></tr>
                <% } %>
            </tbody>
        </table>
    </div>

    <div class="footer">
        Brennero Logistics S.p.A. - Portale Ordini v1.0
    </div>
</body>
</html>
