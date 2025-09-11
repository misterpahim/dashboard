
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector as mysql
from datetime import date

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def db():
    return mysql.connect(host="db", user="root", password="secret", database="casting")

@app.get("/kpi/efficiency")
def efficiency(date_from: date, date_to: date):
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT report_date, sheet_name, metric_value
                    FROM fact_daily_kpi
                    WHERE metric_code='EFFICIENCY'
                    AND report_date BETWEEN %s AND %s
                    ORDER BY report_date, sheet_name""", (date_from, date_to))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows
