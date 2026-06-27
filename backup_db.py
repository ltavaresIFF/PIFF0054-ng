"""
Script de backup do banco de dados SQL Server (Projeto_54).

Gera um arquivo .bak com timestamp na pasta backups/ do projeto.
Utiliza as credenciais/configuracoes definidas em .env (ou defaults).

Uso:
    python backup_db.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

import pyodbc

# Garante que o src está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import SETTINGS


def _build_connection_string() -> str:
    if SETTINGS.trusted_connection:
        return (
            f"DRIVER={{{SETTINGS.sql_driver}}};"
            f"SERVER={SETTINGS.sql_server};"
            f"DATABASE=master;"
            "Trusted_Connection=yes;"
        )
    return (
        f"DRIVER={{{SETTINGS.sql_driver}}};"
        f"SERVER={SETTINGS.sql_server};"
        "DATABASE=master;"
        f"UID={SETTINGS.sql_username};"
        f"PWD={SETTINGS.sql_password};"
    )


def run_backup() -> str:
    """Executa BACKUP DATABASE e retorna o caminho do arquivo .bak gerado."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    backup_file = os.path.join(backup_dir, f"Projeto_54_{timestamp}.bak")
    database_name = SETTINGS.sql_database

    print(f"[INFO] Conectando ao SQL Server: {SETTINGS.sql_server}")
    print(f"[INFO] Banco de origem: {database_name}")
    print(f"[INFO] Arquivo de destino: {backup_file}")

    conn_str = _build_connection_string()

    try:
        conn = pyodbc.connect(conn_str, timeout=15, autocommit=True)
        cursor = conn.cursor()

        backup_sql = f"""
            BACKUP DATABASE [{database_name}]
            TO DISK = N'{backup_file}'
            WITH INIT,
                 NAME = N'{database_name} - Full Backup ({timestamp})',
                 STATS = 10;
        """

        print("[INFO] Iniciando backup...")
        cursor.execute(backup_sql)

        # Exibe progresso (mensagens informativas do SQL Server)
        while cursor.nextset():
            pass

        cursor.close()
        conn.close()

        # Verifica tamanho do arquivo
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        print(f"[OK] Backup concluido com sucesso!")
        print(f"[OK] Arquivo: {backup_file}")
        print(f"[OK] Tamanho: {size_mb:.2f} MB")

        return backup_file

    except pyodbc.Error as exc:
        print(f"[ERRO] Falha no backup: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    run_backup()
