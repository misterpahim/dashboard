
import sys, re, datetime as dt
import pandas as pd
import mysql.connector as mysql

def excel_col_to_index(col: str) -> int:
    col = col.strip().upper()
    n = 0
    for ch in col:
        n = n*26 + (ord(ch)-ord('A')+1)
    return n-1

def parse_cell_ref(cell_ref: str):
    m = re.match(r'^([A-Za-z]+)(\d+)$', cell_ref.strip())
    if not m:
        raise ValueError(f"Invalid cell ref: {cell_ref}")
    return int(m.group(2))-1, excel_col_to_index(m.group(1))

def detect_report_date(path: str) -> dt.date:
    m = re.search(r'(\d{4}[-_/]\d{1,2}[-_/]\d{1,2})', path)
    if m:
        try:
            return dt.date.fromisoformat(m.group(1).replace('_','-').replace('/','-'))
        except:
            pass
    return dt.date.today()

def main():
    if len(sys.argv) < 6:
        print("Usage: python ingest_kpi.py <excel_path> <db_host> <db_user> <db_pass> <db_name>")
        sys.exit(1)
    excel_path, db_host, db_user, db_pass, db_name = sys.argv[1:6]
    xls = pd.ExcelFile(excel_path)
    report_date = detect_report_date(excel_path)
    metrics = [{'metric_code':'EFFICIENCY','cell_ref':'Z172'}]
    rows = []
    for sheet in xls.sheet_names:
        if not sheet.isdigit(): continue
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        for m in metrics:
            r_idx, c_idx = parse_cell_ref(m['cell_ref'])
            try:
                value = df.iat[r_idx, c_idx]
            except:
                value = None
            rows.append((report_date, sheet, m['metric_code'], float(value) if pd.notna(value) else None))
    conn = mysql.connect(host=db_host, user=db_user, password=db_pass, database=db_name)
    cur = conn.cursor()
    for d, sheet, code, val in rows:
        cur.execute("""
        INSERT INTO fact_daily_kpi (report_date, sheet_name, metric_code, metric_value, source_file)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE metric_value=VALUES(metric_value), loaded_at=NOW()
        """, (d, sheet, code, val, excel_path.split('/')[-1]))
    conn.commit()
    cur.close(); conn.close()
    print(f"Ingested {len(rows)} rows for {report_date}")
if __name__ == "__main__":
    main()
