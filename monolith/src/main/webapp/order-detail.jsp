<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.text.SimpleDateFormat, java.math.BigDecimal" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Dettaglio Ordine</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="header">
        <span class="logo">Brennero Logistics</span>
        <nav>
            <a href="portal?action=orders">Ordini</a>
            <a href="portal?action=customers">Clienti</a>
            <a href="portal?action=report">Report</a>
            <a href="portal?action=newOrder" class="btn btn-small">+ Nuovo Ordine</a>
        </nav>
        <span class="user-info">
            <%= session.getAttribute("nomeCompleto") %>
            | <a href="portal?action=logout">Esci</a>
        </span>
    </div>

    <div class="content">
        <%
            Map<String, Object> ordine = (Map<String, Object>) request.getAttribute("ordine");
            List<Map<String, Object>> righe = (List<Map<String, Object>>) request.getAttribute("righe");
            SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy HH:mm");

            if (ordine == null) {
        %>
            <h2>Ordine non trovato</h2>
            <a href="portal?action=orders" class="btn">Torna alla lista</a>
        <% } else { %>

        <h2>Ordine <%= ordine.get("numeroOrdine") %></h2>

        <div class="dettaglio-grid">
            <div class="dettaglio-sezione">
                <h3>Dati Ordine</h3>
                <table class="tabella-dettaglio">
                    <tr><td>N. Ordine:</td><td><strong><%= ordine.get("numeroOrdine") %></strong></td></tr>
                    <tr><td>Data:</td><td><%= ordine.get("dataOrdine") != null ? sdf.format(ordine.get("dataOrdine")) : "-" %></td></tr>
                    <tr><td>Consegna Prevista:</td><td><%= ordine.get("dataConsegnaPrevista") != null ? sdf.format(ordine.get("dataConsegnaPrevista")) : "-" %></td></tr>
                    <tr><td>Consegna Effettiva:</td><td><%= ordine.get("dataConsegnaEffettiva") != null ? sdf.format(ordine.get("dataConsegnaEffettiva")) : "-" %></td></tr>
                    <tr><td>Stato:</td><td>
                        <span class="stato stato-<%= ordine.get("stato") %>">
                            <%= ordine.get("statoDescrizione") %>
                        </span>
                    </td></tr>
                    <tr><td>Tracking:</td><td><%= ordine.get("tracking") != null ? ordine.get("tracking") : "-" %></td></tr>
                </table>
            </div>

            <div class="dettaglio-sezione">
                <h3>Cliente</h3>
                <table class="tabella-dettaglio">
                    <tr><td>Ragione Sociale:</td><td><strong><%= ordine.get("cliente") %></strong></td></tr>
                    <tr><td>P.IVA:</td><td><%= ordine.get("piva") != null ? ordine.get("piva") : "-" %></td></tr>
                    <tr><td>Indirizzo:</td><td><%= ordine.get("indirizzo") != null ? ordine.get("indirizzo") : "-" %></td></tr>
                    <tr><td>Città:</td><td><%= ordine.get("citta") != null ? ordine.get("citta") : "-" %></td></tr>
                    <tr><td>Email:</td><td><%= ordine.get("emailCliente") != null ? ordine.get("emailCliente") : "-" %></td></tr>
                </table>
            </div>
        </div>

        <!-- Note -->
        <% if (ordine.get("noteInterne") != null) { %>
            <div class="note-box note-interne">
                <strong>Note Interne:</strong> <%= ordine.get("noteInterne") %>
            </div>
        <% } %>
        <% if (ordine.get("noteCliente") != null && !((String)ordine.get("noteCliente")).isEmpty()) { %>
            <div class="note-box">
                <strong>Note Cliente:</strong> <%= ordine.get("noteCliente") %>
            </div>
        <% } %>

        <!-- Righe ordine -->
        <h3>Righe Ordine</h3>
        <table class="tabella-dati">
            <thead>
                <tr>
                    <th>Codice</th>
                    <th>Descrizione</th>
                    <th>Qtà</th>
                    <th>Prezzo Unit.</th>
                    <th>Sconto %</th>
                    <th>Importo</th>
                </tr>
            </thead>
            <tbody>
                <%
                    BigDecimal totaleCalcolato = BigDecimal.ZERO;
                    if (righe != null) {
                        for (Map<String, Object> r : righe) {
                            BigDecimal importoRiga = (BigDecimal) r.get("importoRiga");
                            if (importoRiga != null) totaleCalcolato = totaleCalcolato.add(importoRiga);
                %>
                <tr>
                    <td><%= r.get("codiceProdotto") %></td>
                    <td><%= r.get("descrizione") != null ? r.get("descrizione") : "Prodotto sconosciuto" %></td>
                    <td class="numero"><%= r.get("quantita") %></td>
                    <td class="importo">€ <%= String.format("%,.2f", ((BigDecimal)r.get("prezzoUnitario")).doubleValue()) %></td>
                    <td class="numero"><%= r.get("scontoRiga") %></td>
                    <td class="importo">€ <%= importoRiga != null ? String.format("%,.2f", importoRiga.doubleValue()) : "-" %></td>
                </tr>
                <%
                        }
                    }
                %>
            </tbody>
            <tfoot>
                <tr class="totale-riga">
                    <td colspan="5" class="importo"><strong>Totale (da righe):</strong></td>
                    <td class="importo"><strong>€ <%= String.format("%,.2f", totaleCalcolato.doubleValue()) %></strong></td>
                </tr>
                <tr>
                    <td colspan="5" class="importo">Totale (da testata ordine):</td>
                    <td class="importo">
                        <%
                            BigDecimal totaleTestata = (BigDecimal) ordine.get("importoTotale");
                        %>
                        € <%= totaleTestata != null ? String.format("%,.2f", totaleTestata.doubleValue()) : "-" %>
                        <% if (totaleTestata != null && totaleCalcolato.compareTo(totaleTestata) != 0) { %>
                            <span class="warning" title="Il totale calcolato dalle righe non corrisponde">⚠</span>
                        <% } %>
                    </td>
                </tr>
                <tr>
                    <td colspan="5" class="importo">Sconto cliente:</td>
                    <td class="importo"><%= ordine.get("sconto") %>%</td>
                </tr>
            </tfoot>
        </table>

        <!-- Cambia stato -->
        <% int statoAttuale = (Integer) ordine.get("stato");
           if (statoAttuale < 5) { %>
        <div class="azioni-ordine">
            <h3>Cambia Stato</h3>
            <form method="POST" action="portal" class="form-inline">
                <input type="hidden" name="action" value="updateStatus">
                <input type="hidden" name="idOrdine" value="<%= ordine.get("id") %>">
                <select name="nuovoStato">
                    <option value="0">Bozza</option>
                    <option value="1">Confermato</option>
                    <option value="2">In Lavorazione</option>
                    <option value="3">Spedito</option>
                    <option value="4">Consegnato</option>
                    <option value="5">Annullato</option>
                </select>
                <button type="submit" class="btn">Aggiorna</button>
            </form>
        </div>
        <% } %>

        <a href="portal?action=orders" class="btn">← Torna alla lista</a>

        <% } %>
    </div>

    <div class="footer">
        Brennero Logistics S.p.A. - Portale Ordini v1.0
    </div>
</body>
</html>
