import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import bcrypt as _bcrypt

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH   = os.getenv("DB_PATH", str(BASE_DIR / "brennero.db"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-in-prod")

app = FastAPI(title="Brennero Logistics — Portale Ordini v2")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates  = Jinja2Templates(directory=str(BASE_DIR / "templates"))
engine     = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
def _verify(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------- DB helpers ----------

def get_db():
    with engine.connect() as conn:
        yield conn


def require_auth(request: Request):
    if "username" not in request.session:
        raise HTTPException(status_code=307, headers={"Location": "/login"})
    return request.session


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
    if dataDa:
        q += " AND DATE(o.data_ordine) >= :da"
        params["da"] = dataDa
    if dataA:
        q += " AND DATE(o.data_ordine) <= :a"
        params["a"] = dataA
    q += " ORDER BY o.data_ordine DESC"

    righe = db.execute(text(q), params).fetchall()
    return templates.TemplateResponse(request, "orders.html", {
        "ordini":        righe,
        "stati":         STATI_LABEL,
        "priorita":      PRIORITA_LABEL,
        "filtroCliente": filtroCliente,
        "filtroStato":   filtroStato,
        "dataDa":        dataDa,
        "dataA":         dataA,
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
            SELECT o.*, c.ragione_sociale AS cliente,
                   c.partita_iva, c.pec, c.citta, c.email
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

    return templates.TemplateResponse(request, "order_detail.html", {
        "ordine":      ordine,
        "righe":       righe,
        "stato_label": STATI_LABEL.get(ordine.stato, ordine.stato),
        "stati":       STATI_LABEL,
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


@app.get("/reports", response_class=HTMLResponse)
async def reports(
    request: Request,
    anno: str = "2024",
    db=Depends(get_db),
    _auth=Depends(require_auth),
):
    rows = db.execute(
        text("""
            SELECT c.ragione_sociale AS cliente,
                   COUNT(o.id)          AS num_ordini,
                   SUM(o.importo_netto) AS totale,
                   AVG(o.importo_netto) AS media
            FROM ordini o
            LEFT JOIN clienti c ON o.id_cliente = c.id
            WHERE strftime('%Y', o.data_ordine) = :anno
              AND o.stato != 'annullato'
            GROUP BY o.id_cliente
            ORDER BY totale DESC
        """),
        {"anno": anno},
    ).fetchall()

    stati_count = db.execute(
        text("""
            SELECT stato, COUNT(*) AS cnt
            FROM ordini
            WHERE strftime('%Y', data_ordine) = :anno
            GROUP BY stato
        """),
        {"anno": anno},
    ).fetchall()

    chart_labels = [STATI_LABEL.get(r.stato, r.stato) for r in stati_count]
    chart_data   = [r.cnt for r in stati_count]
    chart_colors = [STATI_CHART_COLORS.get(r.stato, "#aaa") for r in stati_count]

    return templates.TemplateResponse(request, "reports.html", {
        "report":       rows,
        "anno":         anno,
        "chart_labels": chart_labels,
        "chart_data":   chart_data,
        "chart_colors": chart_colors,
    })
