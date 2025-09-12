# app/ingest_oee.py
import openpyxl
import mysql.connector

EXCEL_PATH = "/opt/data/casting.xlsx"

C_DATE = "C6"
C_DIE  = "AM9"
C_MACH = "AO9"
C_ENG  = "AQ9"
C_PROD = "AS9"
C_OTH  = "AU9"
C_OEE  = "AY9"

METRIC_MAP = [
    ("DIE_DOWN_MIN",  C_DIE,  False),
    ("MACH_DOWN_MIN", C_MACH, False),
    ("ENG_DOWN_MIN",  C_ENG,  False),
    ("PROD_DOWN_MIN", C_PROD, False),
    ("OTH_DOWN_MIN",  C_OTH,  False),
    ("OEE_PCT",       C_OEE,  True),
]

def main():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    rows = []
    for name in wb.sheetnames:
        if not name.isdigit(): continue
        ws = wb[name]
        date = ws[C_DATE].value
        if not date: continue
        for code, cell, is_percent in METRIC_MAP:
            v = ws[cell].value
            if v is None: continue
            try:
                val = float(v) * 100.0 if is_percent else float(v)
            except Exception:
                continue
            rows.append((date, code, val))

    conn = mysql.connector.connect(host="db", user="root", password="secret", database="casting")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS kpi_facts (
        report_date DATE NOT NULL,
        metric_code VARCHAR(64) NOT NULL,
        metric_value DOUBLE,
        PRIMARY KEY (report_date, metric_code)
    )""")
    cur.execute("""CREATE OR REPLACE VIEW v_daily_oee AS
        SELECT
          MAX(CASE WHEN metric_code='DIE_DOWN_MIN'  THEN metric_value END) AS die_down_min,
          MAX(CASE WHEN metric_code='MACH_DOWN_MIN' THEN metric_value END) AS mach_down_min,
          MAX(CASE WHEN metric_code='ENG_DOWN_MIN'  THEN metric_value END) AS eng_down_min,
          MAX(CASE WHEN metric_code='PROD_DOWN_MIN' THEN metric_value END) AS prod_down_min,
          MAX(CASE WHEN metric_code='OTH_DOWN_MIN'  THEN metric_value END) AS oth_down_min,
          MAX(CASE WHEN metric_code='OEE_PCT'       THEN metric_value END) AS oee_pct,
          report_date
        FROM kpi_facts
        GROUP BY report_date
    """)
    if rows:
        cur.executemany("""REPLACE INTO kpi_facts (report_date, metric_code, metric_value)
                           VALUES (%s,%s,%s)""", rows)
    conn.commit(); cur.close(); conn.close()
    print(f"Ingested {len(rows)//6} days, {len(rows)} rows.")

if __name__ == "__main__":
    main()
