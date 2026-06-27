"""
Migração dos dados do banco Projeto_54 para o novo esquema Projeto_54_ng.

Mapeamento:
  - Cilindros (1..13)  →  dbo.Cilindros
  - Cilindro_XX_Estático  →  dbo.Ensaios_Estaticos
  - Cilindro_XX          →  dbo.Ensaios_Dados_Dinamicos
  - SysMsgs              →  mantido no banco antigo (apenas 1 registro de sistema)
"""

from __future__ import annotations

import pyodbc

# ---- Configuração de conexão ----
OLD_CS = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Projeto_54;"
    "UID=sa;"
    "PWD=P@ssw0rd_Projeto54!;"
    "TrustServerCertificate=yes;"
)

NEW_CS = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Projeto_54_ng;"
    "UID=sa;"
    "PWD=P@ssw0rd_Projeto54!;"
    "TrustServerCertificate=yes;"
)


def get_conn(cs: str) -> pyodbc.Connection:
    return pyodbc.connect(cs, timeout=30)


def migrate():
    old = get_conn(OLD_CS)
    new = get_conn(NEW_CS)
    old_cursor = old.cursor()
    new_cursor = new.cursor()

    print("=" * 60)
    print("INICIANDO MIGRAÇÃO Projeto_54 → Projeto_54_ng")
    print("=" * 60)

    # --------------------------------------------------
    # 1. CILINDROS
    # --------------------------------------------------
    print("\n[1/4] Migrando Cilindros...")
    cilindros_inseridos = 0
    for i in range(1, 14):
        nome = f"Cilindro {i:02d}"
        # Verifica se já existe (permite reexecução segura)
        new_cursor.execute(
            "SELECT COUNT(*) FROM dbo.Cilindros WHERE Nome_Cilindro = ?", (nome,)
        )
        if new_cursor.fetchone()[0] == 0:
            new_cursor.execute(
                "INSERT INTO dbo.Cilindros (Nome_Cilindro, Capacidade_Sensor, CreatedAt) "
                "OUTPUT INSERTED.Cilindro_ID VALUES (?, NULL, GETDATE())",
                (nome,),
            )
            cilindros_inseridos += 1
    new.commit()
    print(f"  ✓ {cilindros_inseridos} cilindros inseridos")

    # --------------------------------------------------
    # 2. ENSAIOS ESTÁTICOS
    # --------------------------------------------------
    print("\n[2/4] Migrando Ensaios Estáticos...")
    ensaios_inseridos = 0

    for i in range(1, 14):
        tbl_old = f"Cilindro_{i:02d}_Estático"
        try:
            old_cursor.execute(f"SELECT TOP 1 1 FROM {tbl_old}")
        except pyodbc.Error:
            continue  # tabela não existe

        col_id = f"Cilindro_{i:02d}_ID_Teste"
        # Verifica se as colunas esperadas existem (algumas tabelas têm schema diferente)
        old_cursor.execute(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
            (tbl_old,),
        )
        existing_cols = {r[0] for r in old_cursor.fetchall()}
        required = {col_id, "Setpoint", "Tempo_Inicial", "CreatedAt"}
        if not required.issubset(existing_cols):
            print(f"  ⏭ Cilindro {i:02d} — esquema incompatível, pulando")
            continue

        tipo_col = "Tipo_Teste" if "Tipo_Teste" in existing_cols else "NULL"
        status_col = "Status_Ensaio" if "Status_Ensaio" in existing_cols else "NULL"
        duracao_col = "Duracao_Estimada" if "Duracao_Estimada" in existing_cols else "NULL"
        tempo_final_col = "Tempo_Final" if "Tempo_Final" in existing_cols else "NULL"

        old_cursor.execute(f"""
            SELECT
                {i} AS Cilindro,
                [{col_id}] AS Codigo_Teste,
                CAST({tipo_col} AS VARCHAR) AS Tipo_Teste,
                {status_col} AS Status_Ensaio,
                Setpoint,
                {duracao_col} AS Duracao_Estimada,
                Tempo_Inicial,
                {tempo_final_col} AS Tempo_Final,
                CreatedAt
            FROM {tbl_old}
        """)
        cols = [col[0] for col in old_cursor.description]
        for row in old_cursor.fetchall():
            data = dict(zip(cols, row))
            codigo = data["Codigo_Teste"]

            # Pula se já existe
            new_cursor.execute(
                "SELECT COUNT(*) FROM dbo.Ensaios_Estaticos WHERE Codigo_Teste_Negocio = ?",
                (codigo,),
            )
            if new_cursor.fetchone()[0] > 0:
                continue

            # Busca Cilindro_ID
            new_cursor.execute(
                "SELECT Cilindro_ID FROM dbo.Cilindros WHERE Nome_Cilindro = ?",
                (f"Cilindro {data['Cilindro']:02d}",),
            )
            cilindro_id = new_cursor.fetchone()[0]

            # Duracao_Estimada está em horas → converter para segundos
            duracao_h = data.get("Duracao_Estimada") or 0
            duracao_seg = int(round(float(duracao_h) * 3600))

            new_cursor.execute(
                """INSERT INTO dbo.Ensaios_Estaticos
                   (Cilindro_ID, Codigo_Teste_Negocio, Tipo_Teste, Status_Ensaio,
                    Setpoint, Duracao_Estimada_Segundos, Tempo_Inicial, Tempo_Final, CreatedAt)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cilindro_id,
                    codigo,
                    str(data.get("Tipo_Teste") or ""),
                    data.get("Status_Ensaio"),
                    _to_decimal(data.get("Setpoint")),
                    duracao_seg,
                    data.get("Tempo_Inicial"),
                    data.get("Tempo_Final"),
                    data.get("CreatedAt"),
                ),
            )
            ensaios_inseridos += 1

        new.commit()
        print(f"  ✓ Cilindro {i:02d} concluído")

    print(f"  Total: {ensaios_inseridos} ensaios estáticos inseridos")

    # --------------------------------------------------
    # 3. ENSAIOS DADOS DINÂMICOS
    # --------------------------------------------------
    print("\n[3/4] Migrando Dados Dinâmicos...")
    dados_inseridos = 0

    for i in range(1, 14):
        tbl_old = f"Cilindro_{i:02d}"
        col_id_teste = f"Cilindro_{i:02d}_ID_Teste"

        try:
            old_cursor.execute(f"SELECT TOP 1 1 FROM {tbl_old}")
        except pyodbc.Error:
            continue

        # Verifica se a tabela tem dados
        old_cursor.execute(f"SELECT COUNT(*) FROM {tbl_old}")
        if old_cursor.fetchone()[0] == 0:
            continue

        old_cursor.execute(f"""
            SELECT
                [{col_id_teste}] AS Codigo_Teste,
                TimeCol,
                MSecCol,
                LocalCol,
                Setpoint,
                Forca,
                Pressao_Compressor,
                Pressao_Reguladora,
                Temperatura_Ambiente,
                Em_Alarme
            FROM {tbl_old}
            ORDER BY TimeCol
        """)
        cols = [col[0] for col in old_cursor.description]

        batch = []
        for row in old_cursor.fetchall():
            data = dict(zip(cols, row))
            codigo = data["Codigo_Teste"]

            # Lookup Ensaio_ID
            new_cursor.execute(
                "SELECT Ensaio_ID FROM dbo.Ensaios_Estaticos WHERE Codigo_Teste_Negocio = ?",
                (codigo,),
            )
            row_en = new_cursor.fetchone()
            if not row_en:
                print(f"  ⚠ Ensaio não encontrado: {codigo} — pulando")
                continue
            ensaio_id = row_en[0]

            # Converte LocalCol datetime → epoch seconds (INT)
            local_col = data.get("LocalCol")
            if isinstance(local_col, datetime):
                local_col_epoch = int(local_col.timestamp())
            else:
                local_col_epoch = 0

            batch.append((
                ensaio_id,
                data["TimeCol"],
                _to_int(data.get("MSecCol")),
                local_col_epoch,
                _to_decimal(data.get("Setpoint")),
                _to_decimal(data.get("Forca")),
                _to_decimal(data.get("Pressao_Compressor")),
                _to_decimal(data.get("Pressao_Reguladora")),
                _to_decimal(data.get("Temperatura_Ambiente")),
                bool(data.get("Em_Alarme") or False),
            ))

            if len(batch) >= 500:
                new_cursor.executemany(
                    """INSERT INTO dbo.Ensaios_Dados_Dinamicos
                       (Ensaio_ID, TimeCol, MSecCol, LocalCol, Setpoint, Forca,
                        Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Em_Alarme)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    batch,
                )
                dados_inseridos += len(batch)
                batch = []

        # remaining batch
        if batch:
            new_cursor.executemany(
                """INSERT INTO dbo.Ensaios_Dados_Dinamicos
                   (Ensaio_ID, TimeCol, MSecCol, LocalCol, Setpoint, Forca,
                    Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Em_Alarme)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                batch,
            )
            dados_inseridos += len(batch)

        new.commit()
        print(f"  ✓ Cilindro {i:02d} concluído")

    print(f"  Total: {dados_inseridos} registros dinâmicos inseridos")

    # --------------------------------------------------
    # 4. SYSMSGS (opcional - migrar para o novo banco)
    # --------------------------------------------------
    print("\n[4/4] Migrando SysMsgs...")
    old_cursor.execute("SELECT COUNT(*) FROM SysMsgs")
    sys_count = old_cursor.fetchone()[0]
    print(f"  ✓ {sys_count} registro(s) de sistema (mantido no banco original)")
    print("  ℹ SysMsgs é tabela de log do sistema — mantida apenas no banco original")

    # --------------------------------------------------
    # Final
    # --------------------------------------------------
    old.close()
    new.close()

    print("\n" + "=" * 60)
    print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"  Cilindros:           {cilindros_inseridos}")
    print(f"  Ensaios Estáticos:   {ensaios_inseridos}")
    print(f"  Dados Dinâmicos:     {dados_inseridos}")
    print("=" * 60)


# ---- Utilitários ----
from datetime import datetime  # noqa: E402


def _to_decimal(val):
    """Converte valor para Decimal ou None, com arredondamento para 2 casas."""
    if val is None:
        return None
    try:
        from decimal import Decimal, ROUND_HALF_UP
        d = Decimal(str(val))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return None


def _to_int(val):
    """Converte para int ou None."""
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    migrate()
