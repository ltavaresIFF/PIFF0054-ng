"""Script de teste de consulta real ao banco - execucao avulsa."""
import sys
sys.path.insert(0, r'c:\Users\Leonardo\OneDrive\Estudo\Python\Report_PIFF0054-ng')

# Verifica se o fix de escape_identifier esta ativo
from src.infrastructure.sql.safe_sql import escape_identifier
try:
    result = escape_identifier('Cilindro_01_Est\u00e1tico')
    print(f'[CHECK safe_sql OK] escape_identifier retornou: {result}')
except Exception as e:
    print(f'[CHECK safe_sql FALHOU] {e}')

from src.config.settings import SETTINGS
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.repositories import SqlTestQueryRepository
from src.domain.models import TestContext

conn = SqlServerConnection(SETTINGS)
repo = SqlTestQueryRepository(conn)

print("=" * 60)
print("TESTE DE CONSULTA AO BANCO Projeto_54")
print("=" * 60)

for cyl in range(1, 7):
    print(f"\n--- CILINDRO {cyl:02d} ---")
    try:
        ids = repo.list_test_ids(cyl)
        print(f"  IDs encontrados : {len(ids)}")
        if not ids:
            print("  SEM DADOS")
            continue

        first_id = ids[0]
        last_id  = ids[-1]
        print(f"  Primeiro ID : {first_id}")
        print(f"  Ultimo ID   : {last_id}")

        # carga dinamica com primeiro ID
        ctx = TestContext(cyl_num=cyl, test_id=first_id)
        dyn = repo.load_dynamic_rows(ctx)
        print(f"  Linhas din. : {dyn.total_rows}")
        print(f"  Colunas     : {list(dyn.rows.columns)}")
        if not dyn.rows.empty:
            print(f"  Amostra LocalCol[0]: {dyn.rows['LocalCol'].iloc[0]}")

        # carga estatica
        sta = repo.load_static_row(ctx)
        print(f"  Tabela est. : {sta.table_used}")
        print(f"  Colunas est.: {list(sta.row.columns)}")

        # coluna de forca
        fc = repo.detect_force_column(cyl)
        print(f"  Forca col.  : {fc}")

        # variaveis Y disponiveis
        ycols = repo.load_available_y_columns(cyl)
        print(f"  Eixos Y     : {ycols}")

    except Exception as e:
        print(f"  ERRO: {e}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
