"""Profiling isolado de cada passo do load_test + kaleido."""
import time
import pyodbc

CS = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=Projeto_54;Trusted_Connection=yes;"


def measure(label, fn):
    t0 = time.perf_counter()
    result = fn()
    ms = (time.perf_counter() - t0) * 1000
    print(f"  {label:<52}: {ms:6.0f} ms")
    return result


conn = pyodbc.connect(CS, timeout=10)

QCOLS = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION"
QTEX = "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?"
QDATA = "SELECT * FROM [Cilindro_01] WHERE [Cilindro_01_ID_Teste] = ? ORDER BY [LocalCol]"
QSTAT = "SELECT * FROM [Cilindro_01_Est\u00e1tico] WHERE [Cilindro_01_ID_Teste] = ?"


def qfetch(q, p=()):
    cur = conn.cursor()
    cur.execute(q, p)
    return cur.fetchall()


print("\n=== SQL queries (conexao existente, sem fechar) ===")
measure("_get_columns(Cilindro_01) 1a vez", lambda: qfetch(QCOLS, ("Cilindro_01",)))
measure("_get_columns(Cilindro_01) 2a vez", lambda: qfetch(QCOLS, ("Cilindro_01",)))
measure("_get_columns(Cilindro_01) 3a vez", lambda: qfetch(QCOLS, ("Cilindro_01",)))
measure("_table_exists(Cilindro_01_Estatico)", lambda: qfetch(QTEX, ("Cilindro_01_Estatico",)))
measure("_table_exists(Cilindro_01_Estatico acc)", lambda: qfetch(QTEX, ("Cilindro_01_Est\u00e1tico",)))
measure("_get_columns(Cilindro_01_Estatico acc)", lambda: qfetch(QCOLS, ("Cilindro_01_Est\u00e1tico",)))
rows_d = measure("SELECT dynamic 100 rows", lambda: qfetch(QDATA, ("C01_TESTE_001",)))
rows_s = measure("SELECT static row", lambda: qfetch(QSTAT, ("C01_TESTE_001",)))
print(f"    rows_dynamic={len(rows_d)}, rows_static={len(rows_s)}")

conn.close()

print("\n=== Custo de conexao (ODBC pool) ===")
t_all = time.perf_counter()
for i in range(8):
    t0 = time.perf_counter()
    c = pyodbc.connect(CS, timeout=10)
    c.close()
    print(f"  connect+close #{i+1}: {(time.perf_counter()-t0)*1000:.0f} ms")
print(f"  TOTAL 8 conexoes: {(time.perf_counter()-t_all)*1000:.0f} ms")

print("\n=== Kaleido / fig.to_image ===")
import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.DataFrame({"x": range(100), "y": np.random.rand(100)})
fig = go.Figure(go.Scatter(x=df["x"], y=df["y"]))
try:
    t0 = time.perf_counter()
    fig.to_image(format="png", width=1200, height=500)
    print(f"  fig.to_image 1a chamada: {(time.perf_counter()-t0)*1000:.0f} ms")
    t0 = time.perf_counter()
    fig.to_image(format="png", width=1200, height=500)
    print(f"  fig.to_image 2a chamada: {(time.perf_counter()-t0)*1000:.0f} ms")
except Exception as exc:
    print(f"  kaleido nao disponivel: {exc}")

print("\nDone.")
