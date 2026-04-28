import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-prod")

DB_PATH = os.environ.get("DB_PATH", os.path.join(app.root_path, "brennero.db"))


# ---------- DB helpers ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    with open(os.path.join(app.root_path, "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())
    with open(os.path.join(app.root_path, "data.sql"), encoding="utf-8") as f:
        db.executescript(f.read())
    db.close()


# ---------- Auth ----------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


STATI = {
    0: "Bozza",
    1: "Confermato",
    2: "In Lavorazione",
    3: "Spedito",
    4: "Consegnato",
    5: "Annullato",
    6: "Sospeso",
    7: "In Attesa",
}

PRIORITA_LABEL = {1: "Alta", 2: "Media", 3: "Bassa"}


# ---------- Routes ----------

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("orders"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    errore = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        utente = db.execute(
            "SELECT * FROM UTENTI WHERE USERNAME=? AND PASSWORD=? AND FLAG_ATTIVO=1",
            (username, password),
        ).fetchone()
        if utente:
            session["username"] = utente["USERNAME"]
            session["nome_completo"] = utente["NOME_COMPLETO"]
            session["ruolo"] = utente["RUOLO"]
            return redirect(url_for("orders"))
        errore = "Credenziali non valide."
    return render_template("login.html", errore=errore)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/orders")
@login_required
def orders():
    db = get_db()
    filtro_cliente = request.args.get("filtroCliente", "").strip()
    filtro_stato = request.args.get("filtroStato", "").strip()
    data_da = request.args.get("dataDa", "").strip()
    data_a = request.args.get("dataA", "").strip()

    query = """
        SELECT o.ID, o.NUMERO_ORDINE, c.RAGIONE_SOCIALE as cliente,
               o.DATA_ORDINE, o.DATA_CONSEGNA_PREVISTA, o.STATO, o.IMPORTO_TOTALE
        FROM ORDINI o
        LEFT JOIN CLIENTI c ON o.ID_CLIENTE = c.ID
        WHERE 1=1
    """
    params = []
    if filtro_cliente:
        query += " AND c.RAGIONE_SOCIALE LIKE ?"
        params.append(f"%{filtro_cliente}%")
    if filtro_stato != "":
        query += " AND o.STATO = ?"
        params.append(filtro_stato)
    if data_da:
        query += " AND DATE(o.DATA_ORDINE) >= ?"
        params.append(data_da)
    if data_a:
        query += " AND DATE(o.DATA_ORDINE) <= ?"
        params.append(data_a)
    query += " ORDER BY o.DATA_ORDINE DESC"

    righe = db.execute(query, params).fetchall()
    ordini = []
    for r in righe:
        d = dict(r)
        d["stato_label"] = STATI.get(d["STATO"], f"Stato {d['STATO']}")
        ordini.append(d)

    return render_template(
        "orders.html",
        ordini=ordini,
        stati=STATI,
        filtro_cliente=filtro_cliente,
        filtro_stato=filtro_stato,
        data_da=data_da,
        data_a=data_a,
    )


@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    db = get_db()
    ordine = db.execute(
        """SELECT o.*, c.RAGIONE_SOCIALE as cliente, c.PARTITA_IVA, c.CITTA, c.EMAIL
           FROM ORDINI o LEFT JOIN CLIENTI c ON o.ID_CLIENTE = c.ID
           WHERE o.ID = ?""",
        (order_id,),
    ).fetchone()
    if not ordine:
        return "Ordine non trovato", 404

    righe = db.execute(
        """SELECT r.*, p.CODICE, p.DESCRIZIONE, p.TIPO
           FROM RIGHE_ORDINE r LEFT JOIN PRODOTTI p ON r.ID_PRODOTTO = p.ID
           WHERE r.ID_ORDINE = ?""",
        (order_id,),
    ).fetchall()

    stato_label = STATI.get(ordine["STATO"], f"Stato {ordine['STATO']}")
    return render_template(
        "order_detail.html",
        ordine=dict(ordine),
        righe=righe,
        stato_label=stato_label,
        stati=STATI,
    )


@app.route("/customers")
@login_required
def customers():
    db = get_db()
    termine = request.args.get("termine", "").strip()
    query = "SELECT * FROM CLIENTI WHERE FLAG_ATTIVO=1"
    params = []
    if termine:
        query += " AND RAGIONE_SOCIALE LIKE ?"
        params.append(f"%{termine}%")
    query += " ORDER BY RAGIONE_SOCIALE"
    clienti = db.execute(query, params).fetchall()
    return render_template(
        "customers.html",
        clienti=clienti,
        termine=termine,
        priorita_label=PRIORITA_LABEL,
    )


@app.route("/reports")
@login_required
def reports():
    db = get_db()
    anno = request.args.get("anno", "2024")

    # report tabellare per cliente
    rows = db.execute(
        """SELECT c.RAGIONE_SOCIALE as cliente,
                  COUNT(o.ID) as num_ordini,
                  SUM(o.IMPORTO_TOTALE) as totale,
                  AVG(o.IMPORTO_TOTALE) as media
           FROM ORDINI o
           LEFT JOIN CLIENTI c ON o.ID_CLIENTE = c.ID
           WHERE strftime('%Y', o.DATA_ORDINE) = ?
             AND o.STATO != 5
           GROUP BY o.ID_CLIENTE
           ORDER BY totale DESC""",
        (anno,),
    ).fetchall()

    # dati per grafico ordini per stato
    stati_count = db.execute(
        """SELECT STATO, COUNT(*) as cnt
           FROM ORDINI
           WHERE strftime('%Y', DATA_ORDINE) = ?
           GROUP BY STATO""",
        (anno,),
    ).fetchall()
    chart_labels = [STATI.get(r["STATO"], f"Stato {r['STATO']}") for r in stati_count]
    chart_data = [r["cnt"] for r in stati_count]

    return render_template(
        "reports.html",
        report=rows,
        anno=anno,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


# ---------- CLI ----------

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Database inizializzato.")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True)
