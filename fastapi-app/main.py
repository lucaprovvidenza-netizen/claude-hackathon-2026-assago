import os
import secrets
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import bcrypt as _bcrypt

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH   = os.getenv("DB_PATH", str(BASE_DIR / "brennero.db"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-in-prod")

# US-4.2 AC-4: session expires after 30 minutes of inactivity
SESSION_MAX_AGE_SECONDS = int(os.getenv("SESSION_MAX_AGE", "1800"))


# US-4.2 AC-6: security headers on every response
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]        = "DENY"
        response.headers["Referrer-Policy"]        = "strict-origin-when-cross-origin"
        # CSP: allow self + Chart.js asset (already self-hosted in /static)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        return response


app = FastAPI(title="Brennero Logistics — Portale Ordini v2")
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE_SECONDS,
    https_only=False,   # enable in prod
    same_site="lax",
)

@app.exception_handler(401)
async def _redirect_to_login(request: Request, _exc):
    return RedirectResponse(url="/login", status_code=302)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates  = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["csrf_token"] = lambda request: _ensure_csrf(request)
engine     = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# SQLite ignores FK constraints unless enabled per-connection
@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")
def _verify(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------- DB helpers ----------

def get_db():
    with engine.connect() as conn:
        yield conn


def require_auth(request: Request):
    if "username" not in request.session:
        raise HTTPException(status_code=401, detail="Non autenticato")
    return request.session


# US-4.2 AC-3: CSRF token bound to the session.
# - Issued on first GET (via Jinja global `csrf_token`)
# - Verified on every state-changing POST through `verify_csrf` dependency
def _ensure_csrf(request: Request) -> str:
    tok = request.session.get("csrf")
    if not tok:
        tok = secrets.token_urlsafe(32)
        request.session["csrf"] = tok
    return tok


async def verify_csrf(request: Request):
    expected = request.session.get("csrf")
    submitted = None
    try:
        form = await request.form()
        submitted = form.get("csrf_token")
    except Exception:
        pass
    if not expected or not submitted or not secrets.compare_digest(expected, submitted):
        raise HTTPException(status_code=403, detail="CSRF token mancante o non valido")


# ---------- Lookup tables ----------

STATI_LABEL = {
    "bozza":          "Bozza",
    "confermato":     "Confermato",
    "in_lavorazione": "In Lavorazione",
    "spedito":        "Spedito",
    "consegnato":     "Consegnato",
    "annullato":      "Annullato",
}

PRIORITA_LABEL = {
    "bassa":    "Bassa",
    "normale":  "Normale",
    "alta":     "Alta",
    "urgente":  "Urgente",
}

CLASSIFICAZIONE_LABEL = {
    "gold":   "Gold",
    "silver": "Silver",
    "bronze": "Bronze",
}

TIPOLOGIA_LABEL = {
    "TRASPORTO":     "Trasporto",
    "DOGANA":        "Dogana",
    "MAGAZZINO":     "Magazzino",
    "ASSICURAZIONE": "Assicurazione",
    "CONSULENZA":    "Consulenza",
}

# US-1.4: valid state transitions. Empty list = terminal state.
VALID_TRANSITIONS = {
    "bozza":          ["confermato", "annullato"],
    "confermato":     ["in_lavorazione", "annullato"],
    "in_lavorazione": ["spedito"],
    "spedito":        ["consegnato"],
    "consegnato":     [],
    "annullato":      [],
}

STATI_CHART_COLORS = {
    "bozza":          "#dee2e6",
    "confermato":     "#d4edda",
    "in_lavorazione": "#fff3cd",
    "spedito":        "#cce5ff",
    "consegnato":     "#d1ecf1",
    "annullato":      "#f8d7da",
}


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if "username" in request.session:
        return RedirectResponse(url="/orders", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(request, "login.html", {"errore": None})


@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db),
    _csrf=Depends(verify_csrf),
):
    row = db.execute(
        text("SELECT * FROM utenti WHERE username = :u AND attivo = 1"),
        {"u": username},
    ).fetchone()

    if row and _verify(password, row.password_hash):
        request.session["username"]     = row.username
        request.session["nome_completo"] = row.nome_completo
        request.session["ruolo"]        = row.ruolo
        db.execute(
            text("UPDATE utenti SET ultimo_accesso = datetime('now') WHERE username = :u"),
            {"u": username},
        )
        db.commit()
        return RedirectResponse(url="/orders", status_code=302)

    return templates.TemplateResponse(request, "login.html", {"errore": "Credenziali non valide."})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/orders", response_class=HTMLResponse)
async def orders(
    request: Request,
    filtroCliente: str = "",
    filtroStato: str = "",
    filtroTipologia: str = "",
    dataDa: str = "",
    dataA: str = "",
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    q = """
        SELECT o.id, o.numero_ordine,
               c.ragione_sociale AS cliente,
               o.data_ordine, o.data_consegna_prevista,
               o.stato, o.priorita, o.importo_netto
        FROM ordini o
        LEFT JOIN clienti c ON o.id_cliente = c.id
        WHERE 1=1
    """
    params: dict = {}
    if filtroCliente:
        q += " AND c.ragione_sociale LIKE :cliente"
        params["cliente"] = f"%{filtroCliente}%"
    if filtroStato:
        q += " AND o.stato = :stato"
        params["stato"] = filtroStato
    if filtroTipologia:
        q += """ AND EXISTS (
            SELECT 1 FROM righe_ordine r
            JOIN prodotti p ON r.id_prodotto = p.id
            WHERE r.id_ordine = o.id AND p.tipologia = :tipologia
        )"""
        params["tipologia"] = filtroTipologia
    if dataDa:
        q += " AND DATE(o.data_ordine) >= :da"
        params["da"] = dataDa
    if dataA:
        q += " AND DATE(o.data_ordine) <= :a"
        params["a"] = dataA
    q += " ORDER BY o.data_ordine DESC"

    righe = db.execute(text(q), params).fetchall()
    return templates.TemplateResponse(request, "orders.html", {
        "ordini":          righe,
        "stati":           STATI_LABEL,
        "priorita":        PRIORITA_LABEL,
        "tipologie":       TIPOLOGIA_LABEL,
        "filtroCliente":   filtroCliente,
        "filtroStato":     filtroStato,
        "filtroTipologia": filtroTipologia,
        "dataDa":          dataDa,
        "dataA":           dataA,
    })


@app.get("/order/{order_id}", response_class=HTMLResponse)
async def order_detail(
    request: Request,
    order_id: int,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    ordine = db.execute(
        text("""
            SELECT o.*, c.id AS cliente_id, c.ragione_sociale AS cliente,
                   c.partita_iva, c.pec, c.citta, c.email,
                   c.classificazione AS cliente_classificazione
            FROM ordini o
            LEFT JOIN clienti c ON o.id_cliente = c.id
            WHERE o.id = :id
        """),
        {"id": order_id},
    ).fetchone()
    if not ordine:
        raise HTTPException(status_code=404, detail="Ordine non trovato")

    righe = db.execute(
        text("""
            SELECT r.*, p.codice, p.descrizione, p.tipologia
            FROM righe_ordine r
            LEFT JOIN prodotti p ON r.id_prodotto = p.id
            WHERE r.id_ordine = :id
        """),
        {"id": order_id},
    ).fetchall()

    transizioni_valide = {
        s: STATI_LABEL[s] for s in VALID_TRANSITIONS.get(ordine.stato, [])
    }
    return templates.TemplateResponse(request, "order_detail.html", {
        "ordine":             ordine,
        "righe":              righe,
        "stato_label":        STATI_LABEL.get(ordine.stato, ordine.stato),
        "stati":              STATI_LABEL,
        "transizioni_valide": transizioni_valide,
        "cl_label":           CLASSIFICAZIONE_LABEL,
        "errore":             request.query_params.get("errore"),
    })


@app.get("/customers", response_class=HTMLResponse)
async def customers(
    request: Request,
    termine: str = "",
    classificazione: str = "",
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    q = "SELECT * FROM clienti WHERE attivo = 1"
    params: dict = {}
    if termine:
        q += " AND ragione_sociale LIKE :t"
        params["t"] = f"%{termine}%"
    if classificazione:
        q += " AND classificazione = :cl"
        params["cl"] = classificazione
    q += " ORDER BY ragione_sociale"

    clienti = db.execute(text(q), params).fetchall()
    return templates.TemplateResponse(request, "customers.html", {
        "clienti":         clienti,
        "termine":         termine,
        "classificazione": classificazione,
        "cl_label":        CLASSIFICAZIONE_LABEL,
    })


# ---------- E2: Customer detail / edit ----------

@app.get("/customer/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    request: Request,
    customer_id: int,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    cliente = db.execute(
        text("SELECT * FROM clienti WHERE id = :id"),
        {"id": customer_id},
    ).fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    # US-2.1 AC-4: ultimo ordine del cliente
    ultimo = db.execute(
        text("""
            SELECT MAX(data_ordine) AS ultimo
            FROM ordini WHERE id_cliente = :id
        """),
        {"id": customer_id},
    ).fetchone()
    ultimo_ordine = ultimo.ultimo if ultimo else None

    # US-2.1 AC-5: fatturato annuo (anno corrente, esclusi annullati)
    anno_corrente = date.today().year
    fatturato = db.execute(
        text("""
            SELECT COALESCE(SUM(importo_netto), 0) AS tot
            FROM ordini
            WHERE id_cliente = :id
              AND stato != 'annullato'
              AND strftime('%Y', data_ordine) = :anno
        """),
        {"id": customer_id, "anno": str(anno_corrente)},
    ).fetchone()
    fatturato_annuo = float(fatturato.tot or 0)

    return templates.TemplateResponse(request, "customer_detail.html", {
        "cliente":         cliente,
        "ultimo_ordine":   ultimo_ordine,
        "fatturato_annuo": fatturato_annuo,
        "anno_corrente":   anno_corrente,
        "cl_label":        CLASSIFICAZIONE_LABEL,
        "saved":           request.query_params.get("saved"),
    })


@app.post("/customer/{customer_id}/edit")
async def customer_edit(
    request: Request,
    customer_id: int,
    classificazione: str = Form(...),
    note: str = Form(""),
    db=Depends(get_db),
    _auth=Depends(require_auth),
    _csrf=Depends(verify_csrf),
):
    if classificazione not in CLASSIFICAZIONE_LABEL:
        raise HTTPException(status_code=400, detail="Classificazione non valida")

    db.execute(
        text("""
            UPDATE clienti
            SET classificazione = :cl, note = :note, updated_at = datetime('now')
            WHERE id = :id
        """),
        {"cl": classificazione, "note": note or None, "id": customer_id},
    )
    db.commit()
    return RedirectResponse(url=f"/customer/{customer_id}?saved=1", status_code=303)


# ---------- E2: Global search ----------

@app.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str = "",
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    q = q.strip()
    clienti_results: list = []
    prodotti_results: list = []

    if q:
        # US-2.3 AC-7: case-insensitive partial match (LIKE on SQLite is CI for ASCII)
        like = f"%{q}%"
        clienti_results = db.execute(
            text("""
                SELECT id, ragione_sociale, citta, classificazione
                FROM clienti
                WHERE attivo = 1 AND ragione_sociale LIKE :q
                ORDER BY ragione_sociale
                LIMIT 50
            """),
            {"q": like},
        ).fetchall()

        prodotti_results = db.execute(
            text("""
                SELECT id, codice, descrizione, tipologia, prezzo_unitario
                FROM prodotti
                WHERE attivo = 1
                  AND (descrizione LIKE :q OR codice LIKE :q)
                ORDER BY tipologia, codice
                LIMIT 50
            """),
            {"q": like},
        ).fetchall()

    return templates.TemplateResponse(request, "search_results.html", {
        "q":                q,
        "clienti":          clienti_results,
        "prodotti":         prodotti_results,
        "cl_label":         CLASSIFICAZIONE_LABEL,
        "tipologie":        TIPOLOGIA_LABEL,
    })


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(
    request: Request,
    product_id: int,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    p = db.execute(
        text("SELECT * FROM prodotti WHERE id = :id"),
        {"id": product_id},
    ).fetchone()
    if not p:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    return templates.TemplateResponse(request, "product_detail.html", {
        "prodotto":  p,
        "tipologie": TIPOLOGIA_LABEL,
    })


# ---------- E1: Product catalogue ----------

@app.get("/products", response_class=HTMLResponse)
async def products(
    request: Request,
    filtroTipologia: str = "",
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    q = "SELECT * FROM prodotti WHERE attivo = 1"
    params: dict = {}
    if filtroTipologia:
        q += " AND tipologia = :tipologia"
        params["tipologia"] = filtroTipologia
    q += " ORDER BY tipologia, codice"

    prodotti = db.execute(text(q), params).fetchall()
    return templates.TemplateResponse(request, "products.html", {
        "prodotti":        prodotti,
        "tipologie":       TIPOLOGIA_LABEL,
        "filtroTipologia": filtroTipologia,
    })


# ---------- E1: Order creation ----------

def _next_order_number(db, year: int) -> str:
    """Generate ORD-YYYY-NNNN, NNNN = next sequence within the year."""
    row = db.execute(
        text("""
            SELECT COUNT(*) AS n FROM ordini
            WHERE numero_ordine LIKE :prefix
        """),
        {"prefix": f"ORD-{year}-%"},
    ).fetchone()
    return f"ORD-{year}-{(row.n + 1):04d}"


@app.get("/new-order", response_class=HTMLResponse)
async def new_order_get(
    request: Request,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    clienti = db.execute(
        text("SELECT id, ragione_sociale, citta, sconto_default, classificazione "
             "FROM clienti WHERE attivo = 1 ORDER BY ragione_sociale")
    ).fetchall()
    prodotti = db.execute(
        text("SELECT id, codice, descrizione, tipologia, prezzo_unitario, giacenza "
             "FROM prodotti WHERE attivo = 1 ORDER BY tipologia, codice")
    ).fetchall()

    # group by tipologia for the form (US-1.3 AC-1)
    prodotti_per_tipologia: dict = {k: [] for k in TIPOLOGIA_LABEL}
    for p in prodotti:
        prodotti_per_tipologia.setdefault(p.tipologia, []).append(p)

    return templates.TemplateResponse(request, "new_order.html", {
        "clienti":                clienti,
        "prodotti_per_tipologia": prodotti_per_tipologia,
        "tipologie":              TIPOLOGIA_LABEL,
        "errore":                 request.query_params.get("errore"),
    })


@app.post("/save-order")
async def save_order(
    request: Request,
    idCliente: int = Form(...),
    noteCliente: str = Form(""),
    db=Depends(get_db),
    _auth=Depends(require_auth),
    _csrf=Depends(verify_csrf),
):
    form = await request.form()
    prodotti_ids = form.getlist("prodottoId")
    quantita_list = form.getlist("quantita")

    # filter empty/zero rows
    righe_input = []
    for pid, qty in zip(prodotti_ids, quantita_list):
        if not pid or not qty:
            continue
        try:
            pid_i, qty_i = int(pid), int(qty)
        except ValueError:
            continue
        if pid_i > 0 and qty_i > 0:
            righe_input.append((pid_i, qty_i))

    if not righe_input:
        return RedirectResponse(
            url="/new-order?errore=Aggiungi+almeno+una+riga+con+quantità+valida",
            status_code=303,
        )

    cliente = db.execute(
        text("SELECT id, sconto_default FROM clienti WHERE id = :id AND attivo = 1"),
        {"id": idCliente},
    ).fetchone()
    if not cliente:
        return RedirectResponse(url="/new-order?errore=Cliente+non+valido",
                                status_code=303)
    sconto_cliente = float(cliente.sconto_default or 0)

    # validate stock for MAGAZZINO products before opening the transaction
    for pid, qty in righe_input:
        p = db.execute(
            text("SELECT tipologia, giacenza, descrizione FROM prodotti "
                 "WHERE id = :id AND attivo = 1"),
            {"id": pid},
        ).fetchone()
        if not p:
            return RedirectResponse(
                url=f"/new-order?errore=Prodotto+{pid}+non+trovato", status_code=303)
        if p.tipologia == "MAGAZZINO" and p.giacenza is not None and qty > p.giacenza:
            return RedirectResponse(
                url=f"/new-order?errore=Giacenza+insufficiente+per+{p.descrizione}",
                status_code=303,
            )

    today = date.today()
    consegna_prevista = (today + timedelta(days=7)).isoformat()
    username = request.session.get("username", "system")
    numero_ordine = _next_order_number(db, today.year)

    # US-4.3 AC-2: open a dedicated transaction for the whole write — rollback on error
    try:
        with engine.begin() as txn:
            res = txn.execute(
                text("""
                    INSERT INTO ordini (numero_ordine, id_cliente, stato, priorita,
                                        data_ordine, data_consegna_prevista,
                                        importo_lordo, sconto_percentuale, importo_netto,
                                        note_cliente, created_by, updated_by)
                    VALUES (:num, :cli, 'bozza', 'normale',
                            datetime('now'), :consegna,
                            0, :sconto, 0,
                            :note, :user, :user)
                """),
                {"num": numero_ordine, "cli": idCliente,
                 "consegna": consegna_prevista, "sconto": sconto_cliente,
                 "note": noteCliente or None, "user": username},
            )
            id_ordine = res.lastrowid

            importo_lordo = 0.0
            importo_netto = 0.0
            for pid, qty in righe_input:
                p = txn.execute(
                    text("SELECT prezzo_unitario, tipologia, giacenza "
                         "FROM prodotti WHERE id = :id"),
                    {"id": pid},
                ).fetchone()
                prezzo = float(p.prezzo_unitario)
                lordo_riga = prezzo * qty
                importo_riga = round(lordo_riga * (1 - sconto_cliente / 100), 2)
                importo_lordo += lordo_riga
                importo_netto += importo_riga

                txn.execute(
                    text("""
                        INSERT INTO righe_ordine (id_ordine, id_prodotto, quantita,
                                                  prezzo_unitario, sconto_riga, importo_riga)
                        VALUES (:o, :p, :q, :pu, :sr, :ir)
                    """),
                    {"o": id_ordine, "p": pid, "q": qty,
                     "pu": prezzo, "sr": sconto_cliente, "ir": importo_riga},
                )

                # US-1.3 AC-7: only MAGAZZINO products decrement stock
                if p.tipologia == "MAGAZZINO" and p.giacenza is not None:
                    txn.execute(
                        text("UPDATE prodotti SET giacenza = giacenza - :q "
                             "WHERE id = :id"),
                        {"q": qty, "id": pid},
                    )

            txn.execute(
                text("""
                    UPDATE ordini
                    SET importo_lordo = :il, importo_netto = :inet
                    WHERE id = :id
                """),
                {"il": round(importo_lordo, 2),
                 "inet": round(importo_netto, 2),
                 "id": id_ordine},
            )
    except Exception as e:  # engine.begin() rolls back on exception
        return RedirectResponse(
            url=f"/new-order?errore=Errore+creazione+ordine:+{type(e).__name__}",
            status_code=303,
        )

    return RedirectResponse(url=f"/order/{id_ordine}", status_code=303)


# ---------- E1: Order status workflow ----------

@app.post("/order/{order_id}/status")
async def update_status(
    request: Request,
    order_id: int,
    nuovoStato: str = Form(...),
    db=Depends(get_db),
    _auth=Depends(require_auth),
    _csrf=Depends(verify_csrf),
):
    ordine = db.execute(
        text("SELECT stato FROM ordini WHERE id = :id"),
        {"id": order_id},
    ).fetchone()
    if not ordine:
        raise HTTPException(status_code=404, detail="Ordine non trovato")

    # US-1.4 AC-1, AC-2, AC-5: enforce valid transitions
    if nuovoStato not in VALID_TRANSITIONS.get(ordine.stato, []):
        return RedirectResponse(
            url=f"/order/{order_id}?errore=Transizione+non+valida",
            status_code=303,
        )

    username = request.session.get("username", "system")

    # US-1.4 AC-3, AC-4: record updater + set actual delivery on consegnato
    if nuovoStato == "consegnato":
        db.execute(
            text("""
                UPDATE ordini
                SET stato = :s, updated_by = :u,
                    updated_at = datetime('now'),
                    data_consegna_effettiva = datetime('now')
                WHERE id = :id
            """),
            {"s": nuovoStato, "u": username, "id": order_id},
        )
    else:
        db.execute(
            text("""
                UPDATE ordini
                SET stato = :s, updated_by = :u, updated_at = datetime('now')
                WHERE id = :id
            """),
            {"s": nuovoStato, "u": username, "id": order_id},
        )
    db.commit()

    return RedirectResponse(url=f"/order/{order_id}", status_code=303)


CLASSIFICAZIONE_CHART_COLORS = {
    "gold":   "#d4ac0d",
    "silver": "#909497",
    "bronze": "#a04000",
}

# US-3.1 AC-2: stati "in lavorazione" lato dashboard (open orders)
STATI_IN_PROGRESS = ("confermato", "in_lavorazione", "spedito")


def _kpi_for_year(db, anno: int) -> dict:
    """Aggregate KPI for a single year, including archived orders (US-5.3 AC-5)."""
    row = db.execute(
        text("""
            WITH all_orders AS (
                SELECT stato, importo_netto, data_ordine FROM ordini
                UNION ALL
                SELECT stato, importo_netto, data_ordine FROM ordini_archivio
            )
            SELECT
                COUNT(*) FILTER (WHERE stato != 'annullato')                     AS tot,
                COALESCE(SUM(CASE WHEN stato != 'annullato'
                                  THEN importo_netto ELSE 0 END), 0)             AS fatturato,
                COUNT(*) FILTER (WHERE stato IN ('confermato','in_lavorazione','spedito')) AS in_progress,
                AVG(CASE WHEN stato != 'annullato' THEN importo_netto END)       AS media
            FROM all_orders
            WHERE strftime('%Y', data_ordine) = :anno
        """),
        {"anno": str(anno)},
    ).fetchone()
    return {
        "totale":      row.tot or 0,
        "fatturato":   float(row.fatturato or 0),
        "in_progress": row.in_progress or 0,
        "ticket":      float(row.media or 0),
    }


def _delta_pct(curr: float, prev: float) -> Optional[float]:
    """Return % delta or None if base is zero."""
    if not prev:
        return None
    return round((curr - prev) / prev * 100, 1)


# ---------- E5: Data integrity & archive ----------

ARCHIVE_THRESHOLD_DAYS = int(os.getenv("ARCHIVE_THRESHOLD_DAYS", "730"))  # 2 years
ARCHIVABLE_STATES = ("consegnato", "annullato")


@app.get("/admin/integrity-check", response_class=HTMLResponse)
async def integrity_check(
    request: Request,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    """US-5.1 AC-1, AC-2, AC-3: report di discrepanze totale/righe."""
    rows = db.execute(
        text("""
            SELECT o.id,
                   o.numero_ordine,
                   o.importo_netto                                AS testata,
                   COALESCE(SUM(r.importo_riga), 0)               AS righe_sum,
                   COUNT(r.id)                                    AS num_righe,
                   ABS(o.importo_netto - COALESCE(SUM(r.importo_riga), 0)) AS delta
            FROM ordini o
            LEFT JOIN righe_ordine r ON r.id_ordine = o.id
            GROUP BY o.id
            HAVING delta > 0.01
            ORDER BY delta DESC
        """)
    ).fetchall()
    return templates.TemplateResponse(request, "integrity_check.html", {
        "discrepanze": rows,
    })


@app.get("/archive", response_class=HTMLResponse)
async def archive_list(
    request: Request,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    """US-5.3 AC-4: lista ordini archiviati."""
    rows = db.execute(
        text("""
            SELECT a.*, c.ragione_sociale AS cliente, c.classificazione
            FROM ordini_archivio a
            LEFT JOIN clienti c ON a.id_cliente = c.id
            ORDER BY a.archived_at DESC
        """)
    ).fetchall()
    return templates.TemplateResponse(request, "archive.html", {
        "ordini":   rows,
        "stati":    STATI_LABEL,
        "cl_label": CLASSIFICAZIONE_LABEL,
    })


@app.post("/admin/archive")
async def archive_run(
    request: Request,
    db=Depends(get_db),
    _auth=Depends(require_auth),
    _csrf=Depends(verify_csrf),
):
    """US-5.3 AC-2: sposta ordini chiusi più vecchi della soglia in archivio."""
    cutoff = (date.today() - timedelta(days=ARCHIVE_THRESHOLD_DAYS)).isoformat()
    moved = 0
    with engine.begin() as txn:
        eligible = txn.execute(
            text("""
                SELECT id FROM ordini
                WHERE stato IN ('consegnato', 'annullato')
                  AND DATE(data_ordine) < :cutoff
            """),
            {"cutoff": cutoff},
        ).fetchall()

        for row in eligible:
            oid = row.id
            txn.execute(
                text("""
                    INSERT INTO ordini_archivio (
                        id, numero_ordine, id_cliente, stato, priorita,
                        data_ordine, data_consegna_prevista, data_consegna_effettiva,
                        importo_lordo, sconto_percentuale, importo_netto,
                        tipo_spedizione, note_interne, note_cliente, created_by
                    )
                    SELECT id, numero_ordine, id_cliente, stato, priorita,
                           data_ordine, data_consegna_prevista, data_consegna_effettiva,
                           importo_lordo, sconto_percentuale, importo_netto,
                           tipo_spedizione, note_interne, note_cliente, created_by
                    FROM ordini WHERE id = :id
                """),
                {"id": oid},
            )
            txn.execute(
                text("""
                    INSERT INTO righe_ordine_archivio (
                        id, id_ordine, id_prodotto, quantita,
                        prezzo_unitario, sconto_riga, importo_riga, note, created_at
                    )
                    SELECT id, id_ordine, id_prodotto, quantita,
                           prezzo_unitario, sconto_riga, importo_riga, note, created_at
                    FROM righe_ordine WHERE id_ordine = :id
                """),
                {"id": oid},
            )
            txn.execute(text("DELETE FROM righe_ordine WHERE id_ordine = :id"), {"id": oid})
            txn.execute(text("DELETE FROM ordini WHERE id = :id"), {"id": oid})
            moved += 1

    return RedirectResponse(url=f"/archive?moved={moved}", status_code=303)


@app.post("/admin/archive/{order_id}/restore")
async def archive_restore(
    request: Request,
    order_id: int,
    db=Depends(get_db),
    _auth=Depends(require_auth),
    _csrf=Depends(verify_csrf),
):
    """US-5.3 AC-6: ripristina ordine archiviato in tabella operativa."""
    with engine.begin() as txn:
        exists = txn.execute(
            text("SELECT id FROM ordini_archivio WHERE id = :id"),
            {"id": order_id},
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Ordine archiviato non trovato")

        txn.execute(
            text("""
                INSERT INTO ordini (
                    id, numero_ordine, id_cliente, stato, priorita,
                    data_ordine, data_consegna_prevista, data_consegna_effettiva,
                    importo_lordo, sconto_percentuale, importo_netto,
                    tipo_spedizione, note_interne, note_cliente, created_by
                )
                SELECT id, numero_ordine, id_cliente, stato, priorita,
                       data_ordine, data_consegna_prevista, data_consegna_effettiva,
                       importo_lordo, sconto_percentuale, importo_netto,
                       tipo_spedizione, note_interne, note_cliente, created_by
                FROM ordini_archivio WHERE id = :id
            """),
            {"id": order_id},
        )
        txn.execute(
            text("""
                INSERT INTO righe_ordine (
                    id, id_ordine, id_prodotto, quantita,
                    prezzo_unitario, sconto_riga, importo_riga, note, created_at
                )
                SELECT id, id_ordine, id_prodotto, quantita,
                       prezzo_unitario, sconto_riga, importo_riga, note, created_at
                FROM righe_ordine_archivio WHERE id_ordine = :id
            """),
            {"id": order_id},
        )
        txn.execute(text("DELETE FROM righe_ordine_archivio WHERE id_ordine = :id"), {"id": order_id})
        txn.execute(text("DELETE FROM ordini_archivio WHERE id = :id"), {"id": order_id})

    return RedirectResponse(url=f"/order/{order_id}", status_code=303)


@app.get("/reports", response_class=HTMLResponse)
async def reports(
    request: Request,
    anno: int = None,
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    if anno is None:
        anno = date.today().year  # US-3.1 AC-2: default current year

    # available years from operational + archived data (US-5.3 AC-5)
    anni = db.execute(
        text("""
            SELECT DISTINCT strftime('%Y', data_ordine) AS y
            FROM (
                SELECT data_ordine FROM ordini
                UNION ALL
                SELECT data_ordine FROM ordini_archivio
            )
            WHERE y IS NOT NULL
            ORDER BY y DESC
        """)
    ).fetchall()
    anni_lista = [int(r.y) for r in anni if r.y]
    if anno not in anni_lista:
        anni_lista.insert(0, anno)

    kpi      = _kpi_for_year(db, anno)
    kpi_prev = _kpi_for_year(db, anno - 1)
    deltas = {
        "totale":    _delta_pct(kpi["totale"],    kpi_prev["totale"]),
        "fatturato": _delta_pct(kpi["fatturato"], kpi_prev["fatturato"]),
        "ticket":    _delta_pct(kpi["ticket"],    kpi_prev["ticket"]),
    }

    # report tabellare (operational + archived), US-5.3 AC-5
    report_rows = db.execute(
        text("""
            WITH all_orders AS (
                SELECT id, id_cliente, stato, importo_netto, data_ordine
                FROM ordini
                UNION ALL
                SELECT id, id_cliente, stato, importo_netto, data_ordine
                FROM ordini_archivio
            )
            SELECT c.id                 AS cliente_id,
                   c.ragione_sociale    AS cliente,
                   c.classificazione    AS classificazione,
                   COUNT(o.id)          AS num_ordini,
                   SUM(o.importo_netto) AS totale,
                   AVG(o.importo_netto) AS media
            FROM all_orders o
            LEFT JOIN clienti c ON o.id_cliente = c.id
            WHERE strftime('%Y', o.data_ordine) = :anno
              AND o.stato != 'annullato'
            GROUP BY c.id
            ORDER BY totale DESC
        """),
        {"anno": str(anno)},
    ).fetchall()

    # US-3.2: bar chart revenue per customer, sorted desc, colored by classification
    bar_labels = [r.cliente for r in report_rows]
    bar_data   = [round(float(r.totale or 0), 2) for r in report_rows]
    bar_colors = [CLASSIFICAZIONE_CHART_COLORS.get(r.classificazione, "#888")
                  for r in report_rows]
    bar_orders = [r.num_ordini for r in report_rows]

    # US-3.4: donut chart, distribution by status, count + %
    stati_count = db.execute(
        text("""
            WITH all_orders AS (
                SELECT stato, data_ordine FROM ordini
                UNION ALL
                SELECT stato, data_ordine FROM ordini_archivio
            )
            SELECT stato, COUNT(*) AS cnt
            FROM all_orders
            WHERE strftime('%Y', data_ordine) = :anno
            GROUP BY stato
        """),
        {"anno": str(anno)},
    ).fetchall()
    donut_labels = [STATI_LABEL.get(r.stato, r.stato) for r in stati_count]
    donut_data   = [r.cnt for r in stati_count]
    donut_colors = [STATI_CHART_COLORS.get(r.stato, "#aaa") for r in stati_count]

    # US-3.3: line chart, ordini + fatturato per mese
    monthly = db.execute(
        text("""
            WITH all_orders AS (
                SELECT stato, importo_netto, data_ordine FROM ordini
                UNION ALL
                SELECT stato, importo_netto, data_ordine FROM ordini_archivio
            )
            SELECT strftime('%m', data_ordine) AS mese,
                   COUNT(*)                    AS num_ordini,
                   SUM(CASE WHEN stato != 'annullato' THEN importo_netto ELSE 0 END) AS totale
            FROM all_orders
            WHERE strftime('%Y', data_ordine) = :anno
            GROUP BY mese
            ORDER BY mese
        """),
        {"anno": str(anno)},
    ).fetchall()
    monthly_map = {r.mese: r for r in monthly}
    mesi_label = ["Gen","Feb","Mar","Apr","Mag","Giu","Lug","Ago","Set","Ott","Nov","Dic"]
    line_labels = mesi_label
    line_orders   = [monthly_map.get(f"{m:02d}").num_ordini if monthly_map.get(f"{m:02d}") else 0
                     for m in range(1, 13)]
    line_revenue  = [round(float(monthly_map.get(f"{m:02d}").totale or 0), 2)
                     if monthly_map.get(f"{m:02d}") else 0
                     for m in range(1, 13)]

    return templates.TemplateResponse(request, "reports.html", {
        "anno":          anno,
        "anni_lista":    anni_lista,
        "kpi":           kpi,
        "deltas":        deltas,
        "report":        report_rows,
        "cl_label":      CLASSIFICAZIONE_LABEL,
        "bar_labels":    bar_labels,
        "bar_data":      bar_data,
        "bar_colors":    bar_colors,
        "bar_orders":    bar_orders,
        "donut_labels":  donut_labels,
        "donut_data":    donut_data,
        "donut_colors":  donut_colors,
        "line_labels":   line_labels,
        "line_orders":   line_orders,
        "line_revenue":  line_revenue,
    })
