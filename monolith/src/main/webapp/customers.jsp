<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.math.BigDecimal" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Clienti</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <span class="logo">Brennero Logistics</span>
        <nav>
            <a href="portal?action=orders">Ordini</a>
            <a href="portal?action=customers" class="active">Clienti</a>
            <a href="portal?action=report">Report</a>
            <a href="portal?action=newOrder" class="btn btn-small">+ Nuovo Ordine</a>
        </nav>
        <span class="user-info">
            <%= session.getAttribute("nomeCompleto") %>
            | <a href="portal?action=logout">Esci</a>
        </span>
    </div>

    <div class="content">
        <h2>Clienti</h2>

        <form method="GET" action="portal" class="filtri-form">
            <input type="hidden" name="action" value="customers">
            <label>Cerca:
                <input type="text" name="termine"
                       value="<%= request.getAttribute("termine") != null ? request.getAttribute("termine") : "" %>"
                       placeholder="Ragione sociale...">
            </label>
            <button type="submit" class="btn">Cerca</button>
        </form>

        <table class="tabella-dati">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Ragione Sociale</th>
                    <th>P.IVA</th>
                    <th>Città</th>
                    <th>Sconto</th>
                </tr>
            </thead>
            <tbody>
                <%
                    List<Map<String, Object>> clienti = (List<Map<String, Object>>) request.getAttribute("clienti");
                    if (clienti != null) {
                        for (Map<String, Object> c : clienti) {
                %>
                <tr>
                    <td><%= c.get("id") %></td>
                    <td><%= c.get("ragioneSociale") %></td>
                    <td><%= c.get("partitaIva") != null ? c.get("partitaIva") : "-" %></td>
                    <td><%= c.get("citta") != null ? c.get("citta") : "-" %></td>
                    <td>
                        <%
                            BigDecimal sconto = (BigDecimal) c.get("scontoSpeciale");
                            out.print(sconto != null && sconto.doubleValue() > 0
                                ? sconto + "%" : "-");
                        %>
                    </td>
                </tr>
                <%
                        }
                    }
                    if (clienti == null || clienti.isEmpty()) {
                %>
                <tr><td colspan="5" class="vuoto">Nessun cliente trovato</td></tr>
                <% } %>
            </tbody>
        </table>
    </div>

    <div class="footer">
        Brennero Logistics S.p.A. - Portale Ordini v1.0
    </div>
</body>
</html>
