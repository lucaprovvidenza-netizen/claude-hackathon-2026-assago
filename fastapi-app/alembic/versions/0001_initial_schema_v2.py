"""Initial schema (v2): users, customers (E2 fields), products with tipologia,
orders + lines, archive tables.

Revision ID: 0001
Create Date: 2026-04-28
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("PRAGMA journal_mode = WAL")
    op.execute("PRAGMA foreign_keys = ON")

    op.create_table(
        "utenti",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.Text, nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("nome_completo", sa.Text),
        sa.Column("ruolo", sa.Text, nullable=False, server_default="operatore"),
        sa.Column("attivo", sa.Integer, nullable=False, server_default="1"),
        sa.Column("ultimo_accesso", sa.Text),
        sa.Column("created_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("updated_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("ruolo IN ('admin','operatore','magazzino','report')"),
        sa.CheckConstraint("attivo IN (0,1)"),
    )

    op.create_table(
        "clienti",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ragione_sociale", sa.Text, nullable=False),
        sa.Column("partita_iva", sa.Text),
        sa.Column("codice_fiscale", sa.Text),
        sa.Column("pec", sa.Text),
        sa.Column("codice_sdi", sa.Text),
        sa.Column("indirizzo", sa.Text),
        sa.Column("citta", sa.Text),
        sa.Column("cap", sa.Text),
        sa.Column("provincia", sa.Text),
        sa.Column("paese", sa.Text, nullable=False, server_default="IT"),
        sa.Column("telefono", sa.Text),
        sa.Column("email", sa.Text),
        sa.Column("settore_merceologico", sa.Text),
        sa.Column("referente_commerciale", sa.Text),
        sa.Column("telefono_referente", sa.Text),
        sa.Column("sconto_default", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("classificazione", sa.Text, nullable=False, server_default="bronze"),
        sa.Column("attivo", sa.Integer, nullable=False, server_default="1"),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("updated_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("classificazione IN ('gold','silver','bronze')"),
        sa.CheckConstraint("sconto_default >= 0 AND sconto_default <= 100"),
        sa.CheckConstraint("attivo IN (0,1)"),
    )
    op.create_index("idx_clienti_piva",  "clienti", ["partita_iva"])
    op.create_index("idx_clienti_classe","clienti", ["classificazione"])
    op.create_index("idx_clienti_nome",  "clienti", ["ragione_sociale"])

    op.create_table(
        "prodotti",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("codice", sa.Text, nullable=False, unique=True),
        sa.Column("descrizione", sa.Text),
        sa.Column("tipologia", sa.Text, nullable=False, server_default="TRASPORTO"),
        sa.Column("prezzo_unitario", sa.Float, nullable=False),
        sa.Column("aliquota_iva", sa.Integer, nullable=False, server_default="22"),
        sa.Column("categoria", sa.Text),
        sa.Column("giacenza", sa.Integer),
        sa.Column("attivo", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("updated_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("tipologia IN ('TRASPORTO','DOGANA','MAGAZZINO','ASSICURAZIONE','CONSULENZA')"),
        sa.CheckConstraint("aliquota_iva IN (0,4,5,10,22)"),
        sa.CheckConstraint("prezzo_unitario >= 0"),
        sa.CheckConstraint("giacenza IS NULL OR giacenza >= 0"),
        sa.CheckConstraint("attivo IN (0,1)"),
    )
    op.create_index("idx_prodotti_tipologia", "prodotti", ["tipologia"])

    op.create_table(
        "ordini",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("numero_ordine", sa.Text, nullable=False, unique=True),
        sa.Column("id_cliente", sa.Integer, sa.ForeignKey("clienti.id"), nullable=False),
        sa.Column("stato", sa.Text, nullable=False, server_default="bozza"),
        sa.Column("priorita", sa.Text, nullable=False, server_default="normale"),
        sa.Column("data_ordine", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("data_consegna_prevista", sa.Text),
        sa.Column("data_consegna_effettiva", sa.Text),
        sa.Column("importo_lordo", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("sconto_percentuale", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("importo_netto", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("tipo_spedizione", sa.Text, server_default="standard"),
        sa.Column("peso_totale_kg", sa.Float),
        sa.Column("volume_m3", sa.Float),
        sa.Column("id_corriere", sa.Integer),
        sa.Column("tracking", sa.Text),
        sa.Column("note_interne", sa.Text),
        sa.Column("note_cliente", sa.Text),
        sa.Column("created_by", sa.Text),
        sa.Column("updated_by", sa.Text),
        sa.Column("created_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("updated_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("stato IN ('bozza','confermato','in_lavorazione','spedito','consegnato','annullato')"),
        sa.CheckConstraint("priorita IN ('bassa','normale','alta','urgente')"),
        sa.CheckConstraint("tipo_spedizione IN ('standard','express','internazionale','ritiro_magazzino')"),
        sa.CheckConstraint("sconto_percentuale >= 0 AND sconto_percentuale <= 100"),
    )
    op.create_index("idx_ordini_cliente",  "ordini", ["id_cliente"])
    op.create_index("idx_ordini_stato",    "ordini", ["stato"])
    op.create_index("idx_ordini_priorita", "ordini", ["priorita"])

    op.create_table(
        "righe_ordine",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("id_ordine", sa.Integer,
                  sa.ForeignKey("ordini.id", ondelete="CASCADE"), nullable=False),
        sa.Column("id_prodotto", sa.Integer, sa.ForeignKey("prodotti.id"), nullable=False),
        sa.Column("quantita", sa.Integer, nullable=False),
        sa.Column("prezzo_unitario", sa.Float, nullable=False),
        sa.Column("sconto_riga", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("importo_riga", sa.Float, nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.CheckConstraint("quantita > 0"),
        sa.CheckConstraint("prezzo_unitario >= 0"),
        sa.CheckConstraint("sconto_riga >= 0 AND sconto_riga <= 100"),
    )
    op.create_index("idx_righe_ordine", "righe_ordine", ["id_ordine"])

    # E5: archive tables
    op.create_table(
        "ordini_archivio",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("numero_ordine", sa.Text, nullable=False, unique=True),
        sa.Column("id_cliente", sa.Integer, nullable=False),
        sa.Column("stato", sa.Text, nullable=False),
        sa.Column("priorita", sa.Text, nullable=False),
        sa.Column("data_ordine", sa.Text, nullable=False),
        sa.Column("data_consegna_prevista", sa.Text),
        sa.Column("data_consegna_effettiva", sa.Text),
        sa.Column("importo_lordo", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("sconto_percentuale", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("importo_netto", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("tipo_spedizione", sa.Text),
        sa.Column("note_interne", sa.Text),
        sa.Column("note_cliente", sa.Text),
        sa.Column("created_by", sa.Text),
        sa.Column("archived_at", sa.Text, nullable=False, server_default=sa.text("(datetime('now'))")),
    )
    op.create_index("idx_archivio_cliente", "ordini_archivio", ["id_cliente"])

    op.create_table(
        "righe_ordine_archivio",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("id_ordine", sa.Integer,
                  sa.ForeignKey("ordini_archivio.id", ondelete="CASCADE"), nullable=False),
        sa.Column("id_prodotto", sa.Integer, nullable=False),
        sa.Column("quantita", sa.Integer, nullable=False),
        sa.Column("prezzo_unitario", sa.Float, nullable=False),
        sa.Column("sconto_riga", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("importo_riga", sa.Float, nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.Text),
    )


def downgrade() -> None:
    op.drop_table("righe_ordine_archivio")
    op.drop_table("ordini_archivio")
    op.drop_table("righe_ordine")
    op.drop_table("ordini")
    op.drop_table("prodotti")
    op.drop_table("clienti")
    op.drop_table("utenti")
