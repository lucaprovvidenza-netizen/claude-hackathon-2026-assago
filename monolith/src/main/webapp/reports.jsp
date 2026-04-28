<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.math.BigDecimal" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Report</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <span class="logo">Brennero Logistics</span>
        <nav>
            <a href="portal?action=orders">Ordini</a>
            <a href="portal?action=customers">Clienti</a>
            <a href="portal?action=report" class="active">Report</a>
            <a href="portal?action=newOrder" class="btn btn-small">+ Nuovo Ordine</a>
        </nav>
        <span class="user-info">
            <%= session.getAttribute("nomeCompleto") %>
            | <a href="portal?action=logout">Esci</a>
        </span>
    </div>

    <div class="content">
        <h2>Report Ordini per Cliente</h2>

        <form method="GET" action="portal" class="filtri-form">
            <input type="hidden" name="action" value="report">
            <label>Anno:
                <input type="number" name="anno" value="<%= request.getAttribute("anno") %>"
                       min="2020" max="2030" class="input-anno">
            </label>
            <button type="submit" class="btn">Genera</button>
        </form>

        <table class="tabella-dati">
            <thead>
                <tr>
                    <th>Cliente</th>
                    <th>N. Ordini</th>
                    <th>Totale</th>
                    <th>Media per Ordine</th>
                </tr>
            </thead>
            <tbody>
                <%
                    List<Map<String, Object>> report = (List<Map<String, Object>>) request.getAttribute("report");
                    BigDecimal grandeTotale = BigDecimal.ZERO;
                    int totOrdini = 0;
                    if (report != null) {
                        for (Map<String, Object> r : report) {
                            BigDecimal totale = (BigDecimal) r.get("totale");
                            if (totale != null) grandeTotale = grandeTotale.add(totale);
                            totOrdini += (Integer) r.get("numOrdini");
                %>
                <tr>
                    <td><%= r.get("cliente") %></td>
                    <td class="numero"><%= r.get("numOrdini") %></td>
                    <td class="importo">€ <%= totale != null ? String.format("%,.2f", totale.doubleValue()) : "-" %></td>
                    <td class="importo">
                        <%
                            BigDecimal media = (BigDecimal) r.get("media");
                            out.print(media != null ? String.format("€ %,.2f", media.doubleValue()) : "-");
                        %>
                    </td>
                </tr>
                <%
                        }
                    }
                    if (report == null || report.isEmpty()) {
                %>
                <tr><td colspan="4" class="vuoto">Nessun dato per l'anno selezionato</td></tr>
                <% } else { %>
                <tr class="totale-riga">
                    <td><strong>TOTALE</strong></td>
                    <td class="numero"><strong><%= totOrdini %></strong></td>
                    <td class="importo"><strong>€ <%= String.format("%,.2f", grandeTotale.doubleValue()) %></strong></td>
                    <td></td>
                </tr>
                <% } %>
            </tbody>
        </table>
    </div>

    <div class="footer">
        Brennero Logistics S.p.A. - Portale Ordini v1.0
    </div>
</body>
</html>
