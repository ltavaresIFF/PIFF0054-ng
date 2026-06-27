"""
Migração Projeto_54 → Projeto_54_HP v2 (clustered direto)

Estratégia:
  Tabela única Leituras com PK CLUSTERED em (Cilindro_ID, Codigo_Teste, RowId)
  → Consulta direta por cilindro + teste, sem JOIN
  → Dados contíguos no disco = máxima velocidade
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import pyodbc

CS = ("DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;"
      "UID=sa;PWD=P@ssw0rd_Projeto54!;TrustServerCertificate=yes;")

OLD = CS + "DATABASE=Projeto_54;"
HP = CS + "DATABASE=Projeto_54_HP;"


def dec(val) -> Decimal | None:
    if val is None: return None
    try: return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except: return None

def dec5(val) -> Decimal | None:
    if val is None: return None
    try: return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except: return None


def main():
    old = pyodbc.connect(OLD, timeout=30)
    hp = pyodbc.connect(HP, timeout=30)
    co = old.cursor()
    ch = hp.cursor()

    print("=" * 60)
    print("MIGRAÇÃO → Projeto_54_HP v2")
    print("=" * 60)

    # ---- 1. CILINDROS ----
    print("\n[1/3] Populando Cilindros...")
    cil_map = {}
    for i in range(1, 14):
        nome = f"Cilindro {i:02d}"
        ch.execute("INSERT INTO dbo.Cilindros (Nome_Cilindro) OUTPUT INSERTED.Cilindro_ID VALUES (?)", (nome,))
        cid = ch.fetchone()[0]
        cil_map[i] = cid
    hp.commit()
    print(f"  13 cilindros inseridos (ID 1..13)")

    # ---- 2. LEITURAS (dados + meta) ----
    print("\n[2/3] Migrando Leituras...")
    total = 0
    batch = []

    for i in range(1, 14):
        tbl_d = f"Cilindro_{i:02d}"
        col_id = f"Cilindro_{i:02d}_ID_Teste"
        tbl_e = f"Cilindro_{i:02d}_Estático"

        try:
            co.execute(f"SELECT COUNT(*) FROM {tbl_d}")
            if co.fetchone()[0] == 0:
                continue
        except:
            continue

        # Check colunas disponíveis
        co.execute(f"SELECT TOP 1 * FROM {tbl_d}")
        cols_d = {desc[0] for desc in co.description}
        if col_id not in cols_d:
            continue

        has_obs = "OBS" in cols_d
        has_user = "UserCol" in cols_d
        has_reason = "ReasonCol" in cols_d
        has_leitura = "LeituraIndice" in cols_d
        has_tipo = "Tipo_Teste" in cols_d

        # Meta columns from static table
        meta = {}
        try:
            co.execute(f"SELECT TOP 1 * FROM {tbl_e}")
            cols_e = {desc[0] for desc in co.description}
            has_static = True
        except:
            has_static = False

        if has_static:
            col_setpoint = "Setpoint" if "Setpoint" in cols_e else "NULL"
            col_duracao = "Duracao_Estimada" if "Duracao_Estimada" in cols_e else "NULL"
            col_sensor = "Sensor_Cap" if "Sensor_Cap" in cols_e else "NULL"
            col_temp_ini = "Temperatura_Inicial" if "Temperatura_Inicial" in cols_e else "NULL"
            col_t_ini = "Tempo_Inicial" if "Tempo_Inicial" in cols_e else "NULL"
            col_t_fim = "Tempo_Final" if "Tempo_Final" in cols_e else "NULL"
            col_status = "Status_Ensaio" if "Status_Ensaio" in cols_e else "NULL"

            try:
                co.execute(f"""
                    SELECT [{col_id}] as Codigo,
                           {col_setpoint} as SP, {col_duracao} as Dur,
                           {col_sensor} as Sensor, {col_temp_ini} as TmpIni,
                           {col_t_ini} as TIni, {col_t_fim} as TFim,
                           {col_status} as Status
                    FROM {tbl_e}
                """)
                for r in co.fetchall():
                    meta[r[0]] = {
                        "setpoint": r[1], "duracao": r[2], "sensor": r[3],
                        "temp_ini": r[4], "t_ini": r[5], "t_fim": r[6], "status": r[7]
                    }
            except:
                pass

        # Read dynamic data
        select_cols = f"[{col_id}], [TimeCol], [MSecCol], [LocalCol], [Setpoint], [Forca], [Pressao_Compressor], [Pressao_Reguladora], [Temperatura_Ambiente], [Em_Alarme], [RowId], [CreatedAt]"
        if has_user: select_cols += ", [UserCol]"
        if has_reason: select_cols += ", [ReasonCol]"
        if has_leitura: select_cols += ", [LeituraIndice]"
        if has_tipo: select_cols += ", [Tipo_Teste]"
        if has_obs: select_cols += ", [OBS], [val_obs], [y_column_name]"

        co.execute(f"SELECT {select_cols} FROM {tbl_d} ORDER BY TimeCol")
        db_cols = [desc[0] for desc in co.description]

        for row in co.fetchall():
            data = dict(zip(db_cols, row))
            codigo = data[col_id]
            m = meta.get(codigo, {})

            local_col = data.get("LocalCol")
            if isinstance(local_col, datetime):
                local_col_epoch = int(local_col.timestamp())
            else:
                local_col_epoch = int(local_col) if local_col else 0

            tipo = data.get("Tipo_Teste")
            if tipo is not None:
                try: tipo = int(tipo)
                except: tipo = 0
            dur = m.get("duracao")
            if dur: dur = Decimal(str(dur)).quantize(Decimal("0.01"))

            batch.append((
                i,  # Cilindro_ID (1..13)
                codigo,
                int(data["RowId"]),
                data["TimeCol"],
                int(data["MSecCol"]) if data.get("MSecCol") is not None else None,
                local_col_epoch,
                str(data.get("UserCol") or "") if has_user else None,
                str(data.get("ReasonCol") or "") if has_reason else "",
                dec(data.get("Setpoint")),
                dec(data.get("Forca")),
                dec(data.get("Pressao_Compressor")),
                dec(data.get("Pressao_Reguladora")),
                dec5(data.get("Temperatura_Ambiente")),
                tipo if has_tipo else None,
                int(data.get("LeituraIndice")) if has_leitura and data.get("LeituraIndice") is not None else None,
                bool(data.get("Em_Alarme") or False),
                data.get("CreatedAt") or datetime.now(),
                str(data.get("OBS") or "") if has_obs and data.get("OBS") else None,
                dec(data.get("val_obs")) if has_obs else None,
                str(data.get("y_column_name") or "") if has_obs and data.get("y_column_name") else None,
                str(m.get("sensor") or "") if m.get("sensor") else None,
                str(m.get("status") or "") if m.get("status") else None,
                dur,
                dec5(m.get("temp_ini")),
                m.get("t_ini"),
                m.get("t_fim"),
            ))

            if len(batch) >= 500:
                ch.executemany("""
                    INSERT INTO dbo.Leituras
                        (Cilindro_ID, Codigo_Teste, RowId, TimeCol, MSecCol, LocalCol,
                         UserCol, ReasonCol, Setpoint, Forca,
                         Pressao_Compressor, Pressao_Reguladora,
                         Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                         Em_Alarme, CreatedAt, OBS, val_obs, y_column_name,
                         Sensor_Cap, Status_Ensaio, Duracao_Estimada_Horas,
                         Temperatura_Inicial, Tempo_Inicial, Tempo_Final)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, batch)
                total += len(batch)
                batch = []

        if batch:
            ch.executemany("""
                INSERT INTO dbo.Leituras
                    (Cilindro_ID, Codigo_Teste, RowId, TimeCol, MSecCol, LocalCol,
                     UserCol, ReasonCol, Setpoint, Forca,
                     Pressao_Compressor, Pressao_Reguladora,
                     Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                     Em_Alarme, CreatedAt, OBS, val_obs, y_column_name,
                     Sensor_Cap, Status_Ensaio, Duracao_Estimada_Horas,
                     Temperatura_Inicial, Tempo_Inicial, Tempo_Final)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            total += len(batch)
            batch = []

        hp.commit()
        print(f"  Cilindro {i:02d}: OK")

    print(f"  Total: {total} leituras migradas")

    old.close()
    hp.close()
    print(f"\n{'='*60}")
    print("MIGRAÇÃO CONCLUÍDA!")
    print(f"  Cilindros: 13")
    print(f"  Leituras:  {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
