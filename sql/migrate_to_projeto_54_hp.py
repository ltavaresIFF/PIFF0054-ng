"""
Migração Projeto_54 → Projeto_54_HP (High Performance)

Estratégia:
  1. Cilindros: 13 registros únicos
  2. Ensaios: 300 registros dos Cilindro_XX_Estático
  3. Leituras: 30.000 registros, clusterizados por (Ensaio_ID, RowId)
     → Dados contíguos no disco = clustered seek, sem key lookup
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import pyodbc

CS = ("DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;"
      "UID=sa;PWD=P@ssw0rd_Projeto54!;TrustServerCertificate=yes;")

OLD = CS + "DATABASE=Projeto_54;"
NEW = CS + "DATABASE=Projeto_54_HP;"


def dec(val) -> Decimal | None:
    if val is None:
        return None
    try:
        d = Decimal(str(val))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except:
        return None


def dec5(val) -> Decimal | None:
    if val is None:
        return None
    try:
        d = Decimal(str(val))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except:
        return None


def main():
    old = pyodbc.connect(OLD, timeout=30)
    new = pyodbc.connect(NEW, timeout=30)
    co = old.cursor()
    cn = new.cursor()

    print("=" * 60)
    print("MIGRAÇÃO Projeto_54 → Projeto_54_HP")
    print("=" * 60)

    # ---- 1. CILINDROS ----
    print("\n[1/3] Migrando Cilindros...")
    for i in range(1, 14):
        nome = f"Cilindro {i:02d}"
        cn.execute("INSERT INTO dbo.Cilindros (Nome_Cilindro) OUTPUT INSERTED.Cilindro_ID VALUES (?)", (nome,))
        _ = cn.fetchone()[0]
    new.commit()
    print("  13 cilindros inseridos")

    # ---- 2. ENSAIOS ----
    print("\n[2/3] Migrando Ensaios...")
    total_ensaios = 0
    for i in range(1, 14):
        tbl_e = f"Cilindro_{i:02d}_Estático"
        col_id = f"Cilindro_{i:02d}_ID_Teste"

        try:
            co.execute(f"SELECT TOP 1 1 FROM {tbl_e}")
        except:
            continue

        # Check columns
        co.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (tbl_e,))
        exist = {r[0] for r in co.fetchall()}

        if col_id not in exist or "Setpoint" not in exist:
            continue

        cols = [col_id, "Cilindro", "Setpoint", "CreatedAt"]
        if "Duracao_Estimada" in exist:
            cols.append("Duracao_Estimada")
        if "Sensor_Cap" in exist:
            cols.append("Sensor_Cap")
        if "Temperatura_Inicial" in exist:
            cols.append("Temperatura_Inicial")
        if "Tempo_Inicial" in exist:
            cols.append("Tempo_Inicial")
        if "Tempo_Final" in exist:
            cols.append("Tempo_Final")
        if "Tipo_Teste" in exist:
            cols.append("Tipo_Teste")
        if "Status_Ensaio" in exist:
            cols.append("Status_Ensaio")

        select_cols = ", ".join(f"[{c}]" for c in cols)
        co.execute(f"SELECT {select_cols} FROM {tbl_e}")

        inserted = 0
        for row in co.fetchall():
            data = dict(zip(cols, row))
            codigo = data[col_id]

            # Lookup Cilindro_ID
            cn.execute("SELECT Cilindro_ID FROM dbo.Cilindros WHERE Nome_Cilindro = ?",
                       (f"Cilindro {i:02d}",))
            cid = cn.fetchone()[0]

            duracao = data.get("Duracao_Estimada")
            if duracao:
                duracao = Decimal(str(duracao)).quantize(Decimal("0.01"))

            tipo = data.get("Tipo_Teste")
            if tipo is not None:
                tipo = int(tipo) if isinstance(tipo, (int, float)) else (
                    0 if str(tipo).strip() == "" else int(str(tipo))
                )

            cn.execute("""
                INSERT INTO dbo.Ensaios 
                    (Cilindro_ID, Codigo_Teste, Sensor_Cap, Tipo_Teste, 
                     Status_Ensaio, Setpoint, Duracao_Estimada_Horas,
                     Temperatura_Inicial, Tempo_Inicial, Tempo_Final, CreatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, codigo,
                str(data.get("Sensor_Cap") or "") if data.get("Sensor_Cap") else None,
                tipo,
                data.get("Status_Ensaio"),
                dec(data.get("Setpoint")),
                duracao,
                dec5(data.get("Temperatura_Inicial")),
                data.get("Tempo_Inicial"),
                data.get("Tempo_Final"),
                data.get("CreatedAt") or datetime.now(),
            ))
            inserted += 1

        new.commit()
        total_ensaios += inserted
        print(f"  Cilindro {i:02d}: {inserted} ensaios")
    print(f"  Total: {total_ensaios} ensaios")

    # ---- 3. LEITURAS ----
    print("\n[3/3] Migrando Leituras...")
    total_leituras = 0
    batch = []

    for i in range(1, 14):
        tbl_d = f"Cilindro_{i:02d}"
        col_id = f"Cilindro_{i:02d}_ID_Teste"

        try:
            co.execute(f"SELECT COUNT(*) FROM {tbl_d}")
            if co.fetchone()[0] == 0:
                continue
        except:
            continue

        # Check columns exist
        co.execute(f"SELECT TOP 1 * FROM {tbl_d}")
        exist = {desc[0] for desc in co.description}

        if col_id not in exist:
            continue

        has_obs = "OBS" in exist and "val_obs" in exist and "y_column_name" in exist
        has_user = "UserCol" in exist
        has_reason = "ReasonCol" in exist
        has_leitura = "LeituraIndice" in exist
        has_tipo = "Tipo_Teste" in exist

        co.execute(f"""
            SELECT 
                [{col_id}], [TimeCol], [MSecCol], [LocalCol],
                [Setpoint], [Forca], [Pressao_Compressor],
                [Pressao_Reguladora], [Temperatura_Ambiente], [Em_Alarme],
                [RowId], [CreatedAt]
                {", [UserCol]" if has_user else ""}
                {", [ReasonCol]" if has_reason else ""}
                {", [LeituraIndice]" if has_leitura else ""}
                {", [Tipo_Teste]" if has_tipo else ""}
                {", [OBS], [val_obs], [y_column_name]" if has_obs else ""}
            FROM {tbl_d}
            ORDER BY TimeCol
        """)
        cols = [desc[0] for desc in co.description]

        for row in co.fetchall():
            data = dict(zip(cols, row))
            codigo = data[col_id]

            cn.execute("SELECT Ensaio_ID FROM dbo.Ensaios WHERE Codigo_Teste = ?", (codigo,))
            r = cn.fetchone()
            if not r:
                continue
            ensaio_id = r[0]

            local_col = data.get("LocalCol")
            if isinstance(local_col, datetime):
                local_col_epoch = int(local_col.timestamp())
            else:
                local_col_epoch = int(local_col) if local_col else 0

            tipo = data.get("Tipo_Teste")
            if tipo is not None:
                tipo = int(tipo) if isinstance(tipo, (int, float)) else (
                    0 if str(tipo).strip() == "" else int(str(tipo))
                )

            batch.append((
                ensaio_id,
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
                tipo,
                int(data.get("LeituraIndice")) if has_leitura and data.get("LeituraIndice") is not None else None,
                bool(data.get("Em_Alarme") or False),
                data.get("CreatedAt") or datetime.now(),
                str(data.get("OBS") or "") if has_obs and data.get("OBS") else None,
                dec(data.get("val_obs")) if has_obs else None,
                str(data.get("y_column_name") or "") if has_obs and data.get("y_column_name") else None,
            ))

            if len(batch) >= 500:
                cn.executemany("""
                    INSERT INTO dbo.Leituras
                        (Ensaio_ID, RowId, TimeCol, MSecCol, LocalCol,
                         UserCol, ReasonCol, Setpoint, Forca,
                         Pressao_Compressor, Pressao_Reguladora,
                         Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                         Em_Alarme, CreatedAt, OBS, val_obs, y_column_name)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, batch)
                total_leituras += len(batch)
                batch = []

        if batch:
            cn.executemany("""
                INSERT INTO dbo.Leituras
                    (Ensaio_ID, RowId, TimeCol, MSecCol, LocalCol,
                     UserCol, ReasonCol, Setpoint, Forca,
                     Pressao_Compressor, Pressao_Reguladora,
                     Temperatura_Ambiente, Tipo_Teste, LeituraIndice,
                     Em_Alarme, CreatedAt, OBS, val_obs, y_column_name)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            total_leituras += len(batch)
            batch = []

        new.commit()
        print(f"  Cilindro {i:02d}: leituras migradas")
    print(f"  Total: {total_leituras} leituras")

    old.close()
    new.close()
    print(f"\n{'='*60}")
    print("MIGRAÇÃO CONCLUÍDA!")
    print(f"  Cilindros: 13")
    print(f"  Ensaios:   {total_ensaios}")
    print(f"  Leituras:  {total_leituras}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
