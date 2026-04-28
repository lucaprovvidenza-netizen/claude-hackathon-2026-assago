<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Brennero Logistics - Login</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h1>Brennero Logistics</h1>
            <h2>Portale Ordini</h2>

            <% if (request.getAttribute("errore") != null) { %>
                <div class="errore"><%= request.getAttribute("errore") %></div>
            <% } %>

            <form method="POST" action="portal">
                <input type="hidden" name="action" value="login">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Accedi</button>
            </form>

            <p class="footer-text">© 2024 Brennero Logistics S.p.A. - v1.0</p>
        </div>
    </div>
</body>
</html>
