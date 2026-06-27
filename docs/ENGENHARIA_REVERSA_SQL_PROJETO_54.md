# Engenharia Reversa do Banco SQL Server Projeto_54

Data da analise: 2026-06-26  
Origem: consultas diretas no SQL Server Express (localhost\\SQLEXPRESS, banco Projeto_54) + leitura do codigo de acesso a dados em Report_PIFF54/modules/dal.py.

## 1) Escopo e metodo

Este documento foi gerado para uso por outro agente de IA.

Escopo considerado nesta versao:
- somente tabelas de cilindro 01 a 06 (dinamicas e estaticas)
- tabelas de 07 a 13 foram desconsideradas neste documento por inconsistencia no numero de colunas em relacao ao padrao adotado para 01 a 06

Objetivos:
- mapear estrutura real do recorte (01 a 06)
- identificar pontos de melhoria de desempenho dentro do recorte
- fornecer plano de implementacao focado no escopo valido

Metodologia aplicada:
- catalogo: sys.tables, INFORMATION_SCHEMA.COLUMNS
- volume: sys.partitions
- integridade: INFORMATION_SCHEMA.TABLE_CONSTRAINTS, sys.foreign_keys
- indices: sys.indexes
- comportamento da aplicacao: leitura do DAL (load_test_ids, load_all_test_data, load_static_record)

## 2) Visao geral do modelo (escopo 01 a 06)

### 2.1 Tabelas em escopo

- dinamicas: Cilindro_01, Cilindro_02, Cilindro_03, Cilindro_04, Cilindro_05, Cilindro_06
- estaticas: Cilindro_01_Estatico/Estatico, Cilindro_02_Estatico/Estatico, Cilindro_03_Estatico/Estatico, Cilindro_04_Estatico/Estatico, Cilindro_05_Estatico/Estatico, Cilindro_06_Estatico/Estatico

### 2.2 Tabelas fora de escopo

- Cilindro_07 a Cilindro_13 (dinamicas e estaticas)
- motivo: inconsistencias de quantidade de colunas em relacao ao modelo usado como referencia neste documento

### 2.3 Volume de dados no escopo

- dinamicas (01 a 06): tipicamente 2.500 linhas por cilindro
- estaticas (01 a 06): tipicamente 25 linhas por cilindro

## 3) Padroes de schema no escopo

### 3.1 Padrao dinamico (exemplo: Cilindro_01)

Colunas principais observadas:
- chave tecnica: RowId (bigint)
- chave de negocio: Cilindro_01_ID_Teste (nvarchar, NOT NULL)
- serie temporal: TimeCol, MSecCol, LocalCol
- sinais: Setpoint, Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente
- estado: Tipo_Teste, LeituraIndice, Em_Alarme, CreatedAt
- observacoes por coordenada: OBS, val_obs, y_column_name

### 3.2 Padrao estatico (exemplo: Cilindro_01_Estatico)

Colunas principais observadas:
- chave de negocio: Cilindro_01_ID_Teste (nvarchar, NOT NULL)
- identificacao: Cilindro, Sensor_Cap, Tipo_Teste, Status_Ensaio
- parametros: Setpoint, Duracao_Estimada, Temperatura_Inicial
- tempos consolidados: Tempo_Inicial, Tempo_Final, Tempo_Decorrido_*
- auditoria: CreatedAt

## 4) Integridade referencial no escopo

- os pares de 01 a 06 apresentam PK e FK
- FK tipica: Cilindro_nn.Cilindro_nn_ID_Teste -> Cilindro_nn_Estatico.Cilindro_nn_ID_Teste

## 5) Indices observados no escopo

### 5.1 Tabelas dinamicas (01 a 06)

Padrao observado:
- PK clustered
- IX_Cilindro_nn_ID_Teste (nonclustered)
- IX_Cilindro_nn_LocalCol (nonclustered)

### 5.2 Tabelas estaticas (01 a 06)

Padrao observado:
- PK clustered
- indice nonclustered filtrado por Cilindro_nn_ID_Teste IS NOT NULL

## 6) Como a aplicacao consulta o banco (impacto em performance)

Padroes de query em modules/dal.py:
- lista de ensaios: SELECT DISTINCT Cilindro_nn_ID_Teste ... ORDER BY Cilindro_nn_ID_Teste
- carga principal: SELECT <colunas> FROM Cilindro_nn WHERE Cilindro_nn_ID_Teste = ?
- ordenacao por tempo no app (python) em parte do fluxo; em alguns casos ha ORDER BY LocalCol
- carga estatica: SELECT * FROM Cilindro_nn_Estatico WHERE Cilindro_nn_ID_Teste = ?
- leitura de metadados: INFORMATION_SCHEMA.COLUMNS

Consequencia no escopo 01 a 06:
- os melhores ganhos estao em indices focados em ID_Teste e LocalCol
- padronizacao de consultas evita custo extra de fallback

## 7) Melhorias de desempenho recomendadas (priorizadas, escopo 01 a 06)

## P0 (alta prioridade)

1. Consolidar indice composto por consulta principal nas dinamicas 01 a 06.
2. Revisar redundancia entre indice simples e indice composto para reduzir custo de manutencao de indice.

Exemplo:

```sql
CREATE NONCLUSTERED INDEX IX_Cilindro_01_ID_Teste_LocalCol
ON dbo.Cilindro_01 (Cilindro_01_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);
```

## P1 (alta prioridade)

1. Manter e validar seletividade dos indices filtrados por ID nas estaticas 01 a 06.
2. Atualizar estatisticas apos seed/carga em lote.

```sql
EXEC sp_updatestats;
```

## P2 (media prioridade)

1. Substituir SELECT * no caminho estatico por lista explicita de colunas.
2. Validar se convem manter ordenacao no SQL ou no app para reduzir custo total de CPU/IO.

## P3 (evolutivo)

1. Criar checklist SQL automatizado para garantir que o recorte 01 a 06 se mantenha consistente.
2. Versionar scripts de indice e manutencao em migracoes idempotentes.

## 8) Plano de implementacao sugerido para outro agente de IA

1. Executar baseline de tempos para consultas do recorte 01 a 06.
2. Aplicar indices compostos por cilindro no recorte.
3. Reavaliar e remover indices redundantes onde houver sobreposicao comprovada.
4. Atualizar estatisticas.
5. Reexecutar benchmark de:
   - DISTINCT ID_Teste
   - carga dinamica por ID_Teste
   - carga estatica por ID_Teste
6. Comparar antes/depois com STATISTICS IO e TIME.

## 9) SQL util para validacao rapida (somente 01 a 06)

```sql
-- Inventario de volumes (escopo)
SELECT t.name AS table_name, SUM(p.rows) AS row_count
FROM sys.tables t
JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0,1)
WHERE t.name IN (
  'Cilindro_01','Cilindro_02','Cilindro_03','Cilindro_04','Cilindro_05','Cilindro_06',
  'Cilindro_01_Estático','Cilindro_02_Estático','Cilindro_03_Estático','Cilindro_04_Estático','Cilindro_05_Estático','Cilindro_06_Estático',
  'Cilindro_01_Estatico','Cilindro_02_Estatico','Cilindro_03_Estatico','Cilindro_04_Estatico','Cilindro_05_Estatico','Cilindro_06_Estatico'
)
GROUP BY t.name
ORDER BY t.name;

-- Constraints (escopo)
SELECT tc.TABLE_NAME, tc.CONSTRAINT_TYPE, tc.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
WHERE tc.TABLE_NAME IN (
  'Cilindro_01','Cilindro_02','Cilindro_03','Cilindro_04','Cilindro_05','Cilindro_06',
  'Cilindro_01_Estático','Cilindro_02_Estático','Cilindro_03_Estático','Cilindro_04_Estático','Cilindro_05_Estático','Cilindro_06_Estático',
  'Cilindro_01_Estatico','Cilindro_02_Estatico','Cilindro_03_Estatico','Cilindro_04_Estatico','Cilindro_05_Estatico','Cilindro_06_Estatico'
)
ORDER BY tc.TABLE_NAME;

-- FKs do recorte
SELECT fk.name AS fk_name, tp.name AS parent_table, cp.name AS parent_column,
       tr.name AS ref_table, cr.name AS ref_column
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
WHERE tp.name IN ('Cilindro_01','Cilindro_02','Cilindro_03','Cilindro_04','Cilindro_05','Cilindro_06')
ORDER BY tp.name;

-- Indices do recorte
SELECT t.name AS table_name, i.name AS index_name, i.type_desc, i.is_unique, i.has_filter, i.filter_definition
FROM sys.tables t
LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.index_id > 0
WHERE t.name IN (
  'Cilindro_01','Cilindro_02','Cilindro_03','Cilindro_04','Cilindro_05','Cilindro_06',
  'Cilindro_01_Estático','Cilindro_02_Estático','Cilindro_03_Estático','Cilindro_04_Estático','Cilindro_05_Estático','Cilindro_06_Estático',
  'Cilindro_01_Estatico','Cilindro_02_Estatico','Cilindro_03_Estatico','Cilindro_04_Estatico','Cilindro_05_Estatico','Cilindro_06_Estatico'
)
ORDER BY t.name, i.name;
```

## 10) Conclusao

Este documento considera apenas as tabelas de cilindro 01 a 06. As tabelas de 07 a 13 foram explicitamente desconsideradas por inconsistencia no numero de colunas. No recorte valido, o banco esta estruturado para consultas eficientes e o maior ganho potencial esta na consolidacao de indices compostos alinhados ao padrao de consulta por ID_Teste + LocalCol.
