"""
Relasjonelt SQLite-datalag for G56 – Strategisk Regnskapsanalyse (v2.0).

Håndterer relasjonene mellom NS 4102 Kontoplan (accounts), Analyseøkter (analysis_runs),
Saldobalanse (trial_balance_entries), Hovedbok (ledger_transactions),
Finansielle nøkkeltall & Lønnsomhetsråd (financial_metrics) og KI-innsikt (ai_insights).
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import pandas as pd

from compliance_engine import map_to_ns4102

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/g56_accounting.db")
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    account_no TEXT PRIMARY KEY,
    account_name TEXT NOT NULL DEFAULT '',
    ns4102_class INTEGER NOT NULL DEFAULT 0,
    ns4102_category TEXT NOT NULL DEFAULT 'Ukjent / Udefinert'
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_hash TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    period_label TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sb_filename TEXT NOT NULL,
    hb_filename TEXT NOT NULL,
    is_reconciled INTEGER NOT NULL,
    discrepancy_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS trial_balance_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES analysis_runs(run_id) ON DELETE CASCADE,
    account_no TEXT NOT NULL REFERENCES accounts(account_no),
    ib REAL NOT NULL DEFAULT 0.0,
    debit REAL NOT NULL DEFAULT 0.0,
    credit REAL NOT NULL DEFAULT 0.0,
    ub REAL NOT NULL DEFAULT 0.0,
    net_hb REAL NOT NULL DEFAULT 0.0,
    calculated_ub REAL NOT NULL DEFAULT 0.0,
    discrepancy REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS ledger_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES analysis_runs(run_id) ON DELETE CASCADE,
    voucher_no TEXT NOT NULL DEFAULT '',
    tx_date TEXT NOT NULL DEFAULT '',
    account_no TEXT NOT NULL REFERENCES accounts(account_no),
    description TEXT NOT NULL DEFAULT '',
    debit REAL NOT NULL DEFAULT 0.0,
    credit REAL NOT NULL DEFAULT 0.0,
    net_amount REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER UNIQUE NOT NULL REFERENCES analysis_runs(run_id) ON DELETE CASCADE,
    revenue REAL NOT NULL DEFAULT 0.0,
    ebit REAL NOT NULL DEFAULT 0.0,
    operating_margin_pct REAL NOT NULL DEFAULT 0.0,
    gross_margin_pct REAL NOT NULL DEFAULT 0.0,
    liquidity_ratio_1 REAL NOT NULL DEFAULT 0.0,
    liquidity_ratio_2 REAL NOT NULL DEFAULT 0.0,
    equity_ratio_pct REAL NOT NULL DEFAULT 0.0,
    roa_tkr_pct REAL NOT NULL DEFAULT 0.0,
    roe_ekr_pct REAL NOT NULL DEFAULT 0.0,
    working_capital REAL NOT NULL DEFAULT 0.0,
    full_metrics_json TEXT NOT NULL,
    recommendations_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS ai_insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER UNIQUE NOT NULL REFERENCES analysis_runs(run_id) ON DELETE CASCADE,
    is_mock INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    commentary_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tb_run_id ON trial_balance_entries(run_id);
CREATE INDEX IF NOT EXISTS idx_hb_run_id_acc ON ledger_transactions(run_id, account_no);
CREATE INDEX IF NOT EXISTS idx_hb_run_id_voucher ON ledger_transactions(run_id, voucher_no);
"""


def _extract_ns4102_class(account_no: str) -> int:
    clean = str(account_no).strip().split(".")[0]
    if clean and clean[0].isdigit():
        first_digit = int(clean[0])
        if 1 <= first_digit <= 8:
            return first_digit
    return 0


class DatabaseManager:
    """
    Håndterer SQLite-tilkobling, skjemainitialisering, SHA-256 deduplikasjon
    og spørringer mot regnskapshistorikk og hovedbok.
    """

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = str(db_path)
        self._is_memory = self.db_path == ":memory:"
        self._memory_conn: Optional[sqlite3.Connection] = None

        if not self._is_memory:
            parent_dir = os.path.dirname(os.path.abspath(self.db_path))
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        else:
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")

        self.init_schema()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Gir en transaksjonssikker SQLite-tilkobling som lukkes umiddelbart etter bruk
        for filbaserte databaser (hindrer Windows fil-lås), men bevares i RAM for ':memory:'.
        """
        if self._is_memory:
            assert self._memory_conn is not None
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(self.db_path, timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def close(self) -> None:
        """Lukker in-memory-tilkobling dersom den er aktiv."""
        if self._memory_conn is not None:
            self._memory_conn.close()
            self._memory_conn = None

    def init_schema(self) -> None:
        """Oppretter alle 6 relasjonstabeller og indekser dersom de ikke eksisterer."""
        with self._connection() as conn:
            conn.executescript(SCHEMA_SQL)

    @staticmethod
    def compute_run_hash(company_name: str, sb_df: pd.DataFrame, hb_df: pd.DataFrame) -> str:
        """
        Beregner en deterministisk SHA-256-hash over selskapsnavn, normalisert saldobalanse
        og normalisert hovedbok for å unngå duplikater ved Streamlit-reruns.
        """
        sb_norm = sb_df.copy()
        hb_norm = hb_df.copy()
        if "Konto" in sb_norm.columns:
            sb_norm["Konto"] = sb_norm["Konto"].astype(str).str.strip()
            sb_norm = sb_norm.sort_values(by="Konto").reset_index(drop=True)
        if "Konto" in hb_norm.columns:
            hb_norm["Konto"] = hb_norm["Konto"].astype(str).str.strip()
            hb_norm = hb_norm.reset_index(drop=True)

        payload = (
            f"company={str(company_name).strip()}|"
            f"sb={sb_norm.to_csv(index=False, float_format='%.4f')}|"
            f"hb={hb_norm.to_csv(index=False, float_format='%.4f')}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def save_or_get_analysis_run(
        self,
        company_name: str,
        period_label: str,
        sb_filename: str,
        hb_filename: str,
        sb_df: pd.DataFrame,
        hb_df: pd.DataFrame,
        recon_result: Dict[str, Any],
        metrics: Dict[str, Any],
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[int, bool]:
        """
        Lagrer en komplett regnskapsanalyse (kontoplan, SB, HB, nøkkeltall og lønnsomhetsråd)
        atomisk i SQLite. Dersom identisk `run_hash` allerede finnes, returneres `(eksisterende_run_id, False)`.
        Returnerer `(run_id, created_new)`.
        """
        run_hash = self.compute_run_hash(company_name, sb_df, hb_df)
        recs = recommendations or []

        with self._connection() as conn:
            existing = conn.execute(
                "SELECT run_id FROM analysis_runs WHERE run_hash = ?",
                (run_hash,),
            ).fetchone()
            if existing is not None:
                return int(existing["run_id"]), False

            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            is_reconciled = 1 if recon_result.get("is_reconciled", False) else 0
            discrepancy_count = int(recon_result.get("discrepancy_count", 0))

            cur = conn.execute(
                """
                INSERT INTO analysis_runs (
                    run_hash, company_name, period_label, created_at,
                    sb_filename, hb_filename, is_reconciled, discrepancy_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_hash,
                    str(company_name or "Selskap AS").strip(),
                    str(period_label or "Ukjent periode").strip(),
                    now_iso,
                    str(sb_filename or "saldobalanse.csv"),
                    str(hb_filename or "hovedbok.csv"),
                    is_reconciled,
                    discrepancy_count,
                ),
            )
            run_id = int(cur.lastrowid)

            # 1. Oppdater/sett inn kontoer (accounts) fra både SB og HB
            account_names: Dict[str, str] = {}
            for source_df in (sb_df, hb_df):
                if "Konto" in source_df.columns:
                    for _, row in source_df.iterrows():
                        acc_no = str(row["Konto"]).strip().split(".")[0]
                        acc_name = str(row.get("Kontonavn", "") or "").strip()
                        if acc_no and (acc_no not in account_names or (not account_names[acc_no] and acc_name)):
                            account_names[acc_no] = acc_name

            recon_table = recon_result.get("reconciliation_table")
            if isinstance(recon_table, pd.DataFrame) and "Konto" in recon_table.columns:
                for _, row in recon_table.iterrows():
                    acc_no = str(row["Konto"]).strip().split(".")[0]
                    acc_name = str(row.get("Kontonavn", "") or "").strip()
                    if acc_no and acc_no not in account_names:
                        account_names[acc_no] = acc_name

            for acc_no, acc_name in account_names.items():
                ns_class = _extract_ns4102_class(acc_no)
                ns_cat = map_to_ns4102(acc_no)
                conn.execute(
                    """
                    INSERT INTO accounts (account_no, account_name, ns4102_class, ns4102_category)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(account_no) DO UPDATE SET
                        account_name = CASE
                            WHEN excluded.account_name != '' THEN excluded.account_name
                            ELSE accounts.account_name
                        END,
                        ns4102_class = excluded.ns4102_class,
                        ns4102_category = excluded.ns4102_category
                    """,
                    (acc_no, acc_name or f"Konto {acc_no}", ns_class, ns_cat),
                )

            # 2. Lagre saldobalanselinjer koblet med avstemmingskolonner
            sb_lookup: Dict[str, Tuple[float, float]] = {}
            if "Konto" in sb_df.columns:
                for _, r in sb_df.iterrows():
                    acc_key = str(r["Konto"]).strip().split(".")[0]
                    d_val = float(pd.to_numeric(r.get("Debet", 0.0), errors="coerce") or 0.0)
                    c_val = float(pd.to_numeric(r.get("Kredit", 0.0), errors="coerce") or 0.0)
                    sb_lookup[acc_key] = (d_val, c_val)

            if isinstance(recon_table, pd.DataFrame) and not recon_table.empty:
                for _, r in recon_table.iterrows():
                    acc_no = str(r["Konto"]).strip().split(".")[0]
                    d_val, c_val = sb_lookup.get(acc_no, (0.0, 0.0))
                    conn.execute(
                        """
                        INSERT INTO trial_balance_entries (
                            run_id, account_no, ib, debit, credit, ub,
                            net_hb, calculated_ub, discrepancy
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            run_id,
                            acc_no,
                            float(r.get("IB", 0.0) or 0.0),
                            d_val,
                            c_val,
                            float(r.get("UB", 0.0) or 0.0),
                            float(r.get("Netto_HB", 0.0) or 0.0),
                            float(r.get("Beregnet_UB", 0.0) or 0.0),
                            float(r.get("Avvik", 0.0) or 0.0),
                        ),
                    )

            # 3. Lagre hovedbokstransaksjoner
            if not hb_df.empty and "Konto" in hb_df.columns:
                tx_rows = []
                for _, r in hb_df.iterrows():
                    acc_no = str(r["Konto"]).strip().split(".")[0]
                    voucher_no = str(r.get("Bilagsnr", "") or "").strip()
                    tx_date = str(r.get("Dato", "") or "").strip()
                    desc = str(r.get("Beskrivelse", r.get("Kontonavn", "")) or "").strip()
                    d_val = float(pd.to_numeric(r.get("Debet", 0.0), errors="coerce") or 0.0)
                    c_val = float(pd.to_numeric(r.get("Kredit", 0.0), errors="coerce") or 0.0)
                    tx_rows.append(
                        (run_id, voucher_no, tx_date, acc_no, desc, d_val, c_val, d_val - c_val)
                    )
                conn.executemany(
                    """
                    INSERT INTO ledger_transactions (
                        run_id, voucher_no, tx_date, account_no,
                        description, debit, credit, net_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    tx_rows,
                )

            # 4. Lagre deterministiske nøkkeltall og lønnsomhetsråd
            conn.execute(
                """
                INSERT INTO financial_metrics (
                    run_id, revenue, ebit, operating_margin_pct, gross_margin_pct,
                    liquidity_ratio_1, liquidity_ratio_2, equity_ratio_pct,
                    roa_tkr_pct, roe_ekr_pct, working_capital,
                    full_metrics_json, recommendations_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    float(metrics.get("driftsinntekter", 0.0)),
                    float(metrics.get("ebit", 0.0)),
                    float(metrics.get("driftsmargin", 0.0)),
                    float(metrics.get("bruttomargin", 0.0)),
                    float(metrics.get("likviditetsgrad_1", 0.0)),
                    float(metrics.get("likviditetsgrad_2", 0.0)),
                    float(metrics.get("egenkapitalandel", 0.0)),
                    float(metrics.get("totalkapitalrentabilitet", 0.0)),
                    float(metrics.get("egenkapitalrentabilitet", 0.0)),
                    float(metrics.get("arbeidskapital", 0.0)),
                    json.dumps(metrics, ensure_ascii=False),
                    json.dumps(recs, ensure_ascii=False),
                ),
            )

            return run_id, True

    def save_ai_insight(self, run_id: int, commentary: Any, is_mock: bool = True) -> None:
        """
        Lagrer eller oppdaterer KI-ledelsesrapporten (`ManagementCommentary`) knyttet til en `run_id`.
        """
        if hasattr(commentary, "model_dump"):
            payload_dict = commentary.model_dump()
        elif isinstance(commentary, dict):
            payload_dict = commentary
        else:
            raise TypeError("commentary må være et Pydantic-objekt eller en dict.")

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO ai_insights (run_id, is_mock, created_at, commentary_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    is_mock = excluded.is_mock,
                    created_at = excluded.created_at,
                    commentary_json = excluded.commentary_json
                """,
                (
                    int(run_id),
                    1 if is_mock else 0,
                    now_iso,
                    json.dumps(payload_dict, ensure_ascii=False),
                ),
            )

    def list_analysis_runs(self) -> pd.DataFrame:
        """
        Returnerer en samlet historikktabell over alle lagrede analyser i SQLite,
        inkludert sentrale nøkkeltall og om KI-rapport er generert.
        """
        query = """
        SELECT
            ar.run_id,
            ar.company_name,
            ar.period_label,
            ar.created_at,
            ar.sb_filename,
            ar.hb_filename,
            ar.is_reconciled,
            ar.discrepancy_count,
            fm.revenue,
            fm.ebit,
            fm.operating_margin_pct,
            fm.gross_margin_pct,
            fm.liquidity_ratio_1,
            fm.liquidity_ratio_2,
            fm.equity_ratio_pct,
            fm.roa_tkr_pct,
            fm.roe_ekr_pct,
            fm.working_capital,
            CASE WHEN ai.insight_id IS NOT NULL THEN 1 ELSE 0 END AS has_ai_report,
            ai.is_mock AS ai_is_mock
        FROM analysis_runs ar
        LEFT JOIN financial_metrics fm ON fm.run_id = ar.run_id
        LEFT JOIN ai_insights ai ON ai.run_id = ar.run_id
        ORDER BY ar.run_id DESC
        """
        with self._connection() as conn:
            rows = conn.execute(query).fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([dict(r) for r in rows])

    def get_run_details(self, run_id: int) -> Optional[Dict[str, Any]]:
        """
        Henter fullstendig lagret informasjon (metadata, SB, HB, metrics, lønnsomhetsråd og KI-rapport)
        for en gitt `run_id`.
        """
        with self._connection() as conn:
            run_row = conn.execute(
                "SELECT * FROM analysis_runs WHERE run_id = ?",
                (int(run_id),),
            ).fetchone()
            if run_row is None:
                return None

            tb_rows = conn.execute(
                """
                SELECT
                    tbe.account_no AS Konto,
                    acc.account_name AS Kontonavn,
                    acc.ns4102_category AS NS4102_Kategori,
                    tbe.ib AS IB,
                    tbe.debit AS Debet,
                    tbe.credit AS Kredit,
                    tbe.ub AS UB,
                    tbe.net_hb AS Netto_HB,
                    tbe.calculated_ub AS Beregnet_UB,
                    tbe.discrepancy AS Avvik
                FROM trial_balance_entries tbe
                JOIN accounts acc ON acc.account_no = tbe.account_no
                WHERE tbe.run_id = ?
                ORDER BY tbe.account_no ASC
                """,
                (int(run_id),),
            ).fetchall()

            hb_rows = conn.execute(
                """
                SELECT
                    lt.voucher_no AS Bilagsnr,
                    lt.tx_date AS Dato,
                    lt.account_no AS Konto,
                    acc.account_name AS Kontonavn,
                    acc.ns4102_category AS NS4102_Kategori,
                    lt.description AS Beskrivelse,
                    lt.debit AS Debet,
                    lt.credit AS Kredit,
                    lt.net_amount AS Netto
                FROM ledger_transactions lt
                JOIN accounts acc ON acc.account_no = lt.account_no
                WHERE lt.run_id = ?
                ORDER BY lt.tx_date ASC, lt.tx_id ASC
                """,
                (int(run_id),),
            ).fetchall()

            fm_row = conn.execute(
                "SELECT full_metrics_json, recommendations_json FROM financial_metrics WHERE run_id = ?",
                (int(run_id),),
            ).fetchone()

            ai_row = conn.execute(
                "SELECT is_mock, created_at, commentary_json FROM ai_insights WHERE run_id = ?",
                (int(run_id),),
            ).fetchone()

        metrics_dict = json.loads(fm_row["full_metrics_json"]) if fm_row else {}
        recs_list = json.loads(fm_row["recommendations_json"]) if fm_row else []
        ai_data = None
        if ai_row is not None:
            ai_data = {
                "is_mock": bool(ai_row["is_mock"]),
                "created_at": ai_row["created_at"],
                "commentary": json.loads(ai_row["commentary_json"]),
            }

        return {
            "metadata": dict(run_row),
            "trial_balance": pd.DataFrame([dict(r) for r in tb_rows]),
            "ledger": pd.DataFrame([dict(r) for r in hb_rows]),
            "metrics": metrics_dict,
            "recommendations": recs_list,
            "ai_insight": ai_data,
        }

    def query_ledger_transactions(
        self,
        run_id: int,
        account_no: Optional[str] = None,
        ns4102_category: Optional[str] = None,
        search_text: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Kjører filtrert SQL-spørring mot Hovedboken med SQLite Window Function
        for deterministisk løpende saldo per konto (IB + kumulativ netto bevegelse).
        """
        base_sql = """
        WITH ledger_with_running AS (
            SELECT
                lt.tx_id,
                lt.voucher_no AS Bilagsnr,
                lt.tx_date AS Dato,
                lt.account_no AS Konto,
                acc.account_name AS Kontonavn,
                acc.ns4102_category AS NS4102_Kategori,
                lt.description AS Beskrivelse,
                lt.debit AS Debet,
                lt.credit AS Kredit,
                lt.net_amount AS Netto,
                COALESCE(tbe.ib, 0.0) + SUM(lt.net_amount) OVER (
                    PARTITION BY lt.account_no
                    ORDER BY lt.tx_date ASC, lt.tx_id ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS Lopende_Saldo
            FROM ledger_transactions lt
            JOIN accounts acc ON acc.account_no = lt.account_no
            LEFT JOIN trial_balance_entries tbe
                ON tbe.run_id = lt.run_id AND tbe.account_no = lt.account_no
            WHERE lt.run_id = ?
        )
        SELECT
            Bilagsnr, Dato, Konto, Kontonavn, NS4102_Kategori,
            Beskrivelse, Debet, Kredit, Netto, Lopende_Saldo
        FROM ledger_with_running
        WHERE 1 = 1
        """
        params: List[Any] = [int(run_id)]

        if account_no and account_no != "Alle":
            base_sql += " AND Konto = ?"
            params.append(str(account_no).strip())

        if ns4102_category and ns4102_category != "Alle":
            base_sql += " AND NS4102_Kategori = ?"
            params.append(str(ns4102_category).strip())

        if search_text and search_text.strip():
            like_val = f"%{search_text.strip()}%"
            base_sql += " AND (Beskrivelse LIKE ? OR Bilagsnr LIKE ? OR Kontonavn LIKE ?)"
            params.extend([like_val, like_val, like_val])

        base_sql += " ORDER BY Dato ASC, tx_id ASC"

        with self._connection() as conn:
            rows = conn.execute(base_sql, params).fetchall()
        if not rows:
            return pd.DataFrame(
                columns=[
                    "Bilagsnr",
                    "Dato",
                    "Konto",
                    "Kontonavn",
                    "NS4102_Kategori",
                    "Beskrivelse",
                    "Debet",
                    "Kredit",
                    "Netto",
                    "Lopende_Saldo",
                ]
            )
        return pd.DataFrame([dict(r) for r in rows])

    def delete_analysis_run(self, run_id: int) -> bool:
        """Sletter en kjøring og alle relaterte rader via ON DELETE CASCADE."""
        with self._connection() as conn:
            cur = conn.execute("DELETE FROM analysis_runs WHERE run_id = ?", (int(run_id),))
            return cur.rowcount > 0
