"""Data manager: loads Excel files into in-memory SQLite and provides safe query execution."""

import re
import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Mapping from Excel filename (without extension) to SQL table name
TABLE_MAP = {
    "Clients": "clients",
    "Invoices": "invoices",
    "InvoiceLineItems": "invoice_line_items",
}

_FORBIDDEN_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH)\b",
    re.IGNORECASE,
)


class DataManager:
    """Loads Excel data into an in-memory SQLite database and exposes read-only query methods."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._load_data(data_dir)

    def _load_data(self, data_dir: Path) -> None:
        for xlsx_name, table_name in TABLE_MAP.items():
            path = data_dir / f"{xlsx_name}.xlsx"
            if not path.exists():
                raise FileNotFoundError(f"Missing data file: {path}")
            df = pd.read_excel(path)
            df.to_sql(table_name, self.conn, index=False, if_exists="replace")

    def get_schema(self) -> str:
        """Return a human-readable schema description for all tables."""
        lines: list[str] = []
        cursor = self.conn.cursor()
        for table_name in TABLE_MAP.values():
            cols = cursor.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            lines.append(f"Table: {table_name}")
            lines.append("-" * 40)
            for col in cols:
                # col: (cid, name, type, notnull, default, pk)
                lines.append(f"  {col[1]:25s} {col[2]}")
            # Show distinct values for low-cardinality text columns
            col_names = [c[1] for c in cols]
            for col in cols:
                col_name, col_type = col[1], col[2]
                if col_type == "TEXT":
                    distinct = cursor.execute(
                        f"SELECT DISTINCT \"{col_name}\" FROM {table_name} ORDER BY \"{col_name}\""
                    ).fetchall()
                    if len(distinct) <= 25:
                        vals = [str(row[0]) for row in distinct]
                        lines.append(f"  {col_name} values: {', '.join(vals)}")
            # Show sample rows
            sample = cursor.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
            if sample:
                lines.append(f"  Sample rows:")
                for row in sample:
                    pairs = ", ".join(f"{c}={v}" for c, v in zip(col_names, row))
                    lines.append(f"    {pairs}")
            lines.append("")
        return "\n".join(lines)

    def get_sample_data(self, table_name: str, n: int = 3) -> dict:
        """Return first N rows from a table as a dict with 'columns' and 'rows' keys."""
        safe_tables = set(TABLE_MAP.values())
        if table_name not in safe_tables:
            return {"error": f"Unknown table '{table_name}'. Available: {sorted(safe_tables)}"}
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (n,))
        columns = [desc[0] for desc in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
        return {"columns": columns, "rows": rows}

    def execute_query(self, sql: str) -> dict:
        """Execute a read-only SQL query. Returns dict with 'columns', 'rows', and 'row_count'."""
        sql = sql.strip().rstrip(";") + ";"
        if _FORBIDDEN_PATTERN.search(sql):
            return {"error": "Only SELECT queries are allowed."}
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = [list(row) for row in cursor.fetchall()]
            return {"columns": columns, "rows": rows, "row_count": len(rows)}
        except Exception as e:
            return {"error": str(e)}

    def get_table_names(self) -> list[str]:
        return sorted(TABLE_MAP.values())
