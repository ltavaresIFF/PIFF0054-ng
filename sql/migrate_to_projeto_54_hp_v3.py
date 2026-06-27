"""
Migração Projeto_54 → Projeto_54_HP v3 (schema final)

Estratégia de performance:
  1. Cilindros: lookup (13 linhas)
  2. Ensaios: metadados com covering index (300 linhas)
  3. Leituras: time-series com CLUSTERED INDEX em (Ensaio_ID, RowId)
     → Mesma largura das tabelas originais
     → Dados contíguos por ensaio
     → 2-passos: lookup Ensaio_ID → clustered seek Leituras
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import pyodbc

CS = ("DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;"
      "UID=sa;PWD=P@ssw0rd_Projeto54!;TrustServerCertificate=yes;")

OLD = CS + "DATABASE=Projeto_54;"
HP  = CS + "DATABASE=Projeto_54_HP;"


def dec(v):
    if v is None: return None
    try: return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except: return None


def main():
    old = pyodbc.connect(OLD, timeout=30)
    hp  = pyodbc.connect(HP, timeout=30)
    co = old.cursor()
    ch = hp.cursor()

    print("=" * 60)
    print("MIGRAÇÃO → Projeto_54_HP v3")
    print("=" * 60)

    # ---- 1. CILINDROS ----
    print("\n[1/3] Cilindros...")
    for i in range(1, 14):
        ch.execute("INSERT INTO dbo.Cilindros (Nome_Cilindro) VALUES (?)",
                   (f"Cilindro {i:02d}",))
    hp.commit()
    print("  13 cilindros inseridos")

    # ---- 2. ENSAIOS ----
    print("\n[2/3] Ensaios...")
    total_ens = 0
    for i in range(1, 14):
        tbl_e = f"Cilindro_{i:02d}_Estático"
        col_id = f"Cilindro_{i:02d}_ID_Teste"
        try:
            co.execute(f"SELECT TOP 1 1 FROM {tbl_e}")
        except:
            continue
        co.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (tbl_e,))
        exist = {r[0] for r in co.fetchall()}
        if col_id not in exist or "Setpoint" not in exist:
            continue

        cols = [col_id]
        for c in ["Cilindro", "Setpoint", "Duracao_Estimada", "Sensor_Cap",
                  "Temperatura_Inicial", "Tempo_Inicial", "Tempo_Final",
                  "Tipo_Teste", "Status_Ensaio", "CreatedAt"]:
            if c in exist: cols.append(c)

        select = ", ".join(f"[{c}]" for c in cols)
        co.execute(f"SELECT {select} FROM {tbl_e}")
        db_cols = [desc[0] for desc in co.description]

        for row in co.fetchall():
            d = dict(zip(db_cols, row))
            cod = d[col_id]
            tipo = d.get("Tipo_Teste")
            if tipo is not None:
                try: tipo = int(tipo)
                except: tipo = None
            dur = d.get("Duracao_Estimada")
            if dur: dur = Decimal(str(dur)).quantize(Decimal("0.01"))
            ch.execute("""
                INSERT INTO dbo.Ensaios
                    (Cilindro_ID, Codigo_Teste, Sensor_Cap, Tipo_Teste,
                     Status_Ensaio, Setpoint, Duracao_Estimada_Horas,
                     Temperatura_Inicial, Tempo_Inicial, Tempo_Final, CreatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, cod,
                  str(d.get("Sensor_Cap") or "") if d.get("Sensor_Cap") else None,
                  tipo,
                  d.get("Status_Ensaio"),
                  dec(d.get("Setpoint")),
                  dur,
                  dec(d.get("Temperatura_Inicial")),
                  d.get("Tempo_Inicial"), d.get("Tempo_Final"),
                  d.get("CreatedAt") or datetime.now()))
            total_ens += 1
        hp.commit()
        print(f"  Cilindro {i:02d}: OK")
    print(f"  Total: {total_ens} ensaios")

    # ---- 3. LEITURAS ----
    print("\n[3/3] Leituras...")
    # Build Ensaio lookup: (Cilindro_ID, Codigo_Teste) → Ensaio_ID
    ch.execute("SELECT Ensaio_ID, Cilindro_ID, Codigo_Teste FROM dbo.Ensaios")
    ens_lookup = {(r[1], r[2]): r[0] for r in ch.fetchall()}

    total_leit = 0
    batch = []
    for i in range(1, 14):
        tbl_d = f"Cilindro_{i:02d}"
        col_id = f"Cilindro_{i:02d}_ID_Teste"
        try:
            co.execute(f"SELECT COUNT(*) FROM {tbl_d}")
            if co.fetchone()[0] == 0: continue
        except: continue

        co.execute(f"SELECT TOP 1 * FROM {tbl_d}")
        exist = {desc[0] for desc in co.description}
        if col_id not in exist: continue

        has_obs = "OBS" in exist
        has_user = "UserCol" in exist
        has_reason = "ReasonCol" in exist
        has_leitura = "LeituraIndice" in exist
        has_tipo = "Tipo_Teste" in exist

        sel = f"[{col_id}], [TimeCol], [MSecCol], [LocalCol], [Setpoint], [Forca], [Pressao_Compressor], [Pressao_Reguladora], [Temperatura_Ambiente], [Em_Alarme], [RowId], [CreatedAt]"
        if has_user: sel += ", [UserCol]"
        if has_reason: sel += ", [ReasonCol]"
        if has_leitura: sel += ", [LeituraIndice]"
        if has_tipo: sel += ", [Tipo_Teste]"
        if has_obs: sel += ", [OBS], [val_obs], [y_column_name]"

        co.execute(f"SELECT {sel} FROM {tbl_d} ORDER BY TimeCol")
        db_cols = [desc[0] for desc in co.description]

        for row in co.fetchall():
            d = dict(zip(db_cols, row))
            cod = d[col_id]
            eid = ens_lookup.get((i, cod))
            if not eid: continue

            local_col = d.get("LocalCol")
            if isinstance(local_col, datetime):
                lc = int(local_col.timestamp())
            else:
                lc = int(local_col) if local_col else 0

            tipo = d.get("Tipo_Teste")
            if tipo is not None:
                try: tipo = int(tipo)
                except: tipo = None

            batch.append((
                eid,
                int(d["RowId"]),
                d["TimeCol"],
                int(d["MSecCol"]) if d.get("MSecCol") is not None else None,
                lc,
                str(d.get("UserCol") or "") if has_user else None,
                str(d.get("ReasonCol") or "") if has_reason else "",
                dec(d.get("Setpoint")),
                dec(d.get("Forca")),
                dec(d.get("Pressao_Compressor")),
                dec(d.get("Pressao_Reguladora")),
                dec(d.get("Temperatura_Ambiente")),
                tipo if has_tipo else None,
                int(d.get("LeituraIndice")) if has_leitura and d.get("LeituraIndice") is not None else None,
                bool(d.get("Em_Alarme") or False),
                d.get("CreatedAt") or datetime.now(),
                str(d.get("OBS") or "") if has_obs and d.get("OBS") else None,
                dec(d.get("val_obs")) if has_obs else None,
                str(d.get("y_column_name") or "") if has_obs and d.get("y_column_name") else None,
            ))

            if len(batch) >= 500:
                ch.executemany("""
                    INSERT INTO dbo.Leituras
                        (Ensaio_ID, RowId, TimeCol, MSecCol, LocalCol,
                         UserCol, ReasonCol, Setpoint, Forca,
                         Pressao_Compressor, Pressao_Reguladora,
                         Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                         Em_Alarme, CreatedAt, OBS, val_obs, y_column_name)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, batch)
                total_leit += len(batch)
                batch = []

        if batch:
            ch.executemany("""
                INSERT INTO dbo.Leituras
                    (Ensaio_ID, RowId, TimeCol, MSecCol, LocalCol,
                     UserCol, ReasonCol, Setpoint, Forca,
                     Pressao_Compressor, Pressao_Reguladora,
                     Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                     Em_Alarme, CreatedAt, OBS, val_obs, y_column_name)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            total_leit += len(batch)
            batch = []

        hp.commit()
        print(f"  Cilindro {i:02d}: OK")

    print(f"  Total: {total_leit} leituras")

    old.close(); hp.close()
    print(f"\n{'='*60}")
    print("MIGRAÇÃO CONCLUÍDA!")
    print(f"  Cilindros: 13")
    print(f"  Ensaios:   {total_ens}")
    print(f"  Leituras:  {total_leit}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
