# Relatório de Performance — PIFF-0054 · Consulta C01_TESTE_001

> **Data:** 2026-06-26  
> **Cilindro:** 1 | **Ensaio:** C01_TESTE_001  
> **Objetivo:** Identificar a causa da lentidão na carga e renderização do gráfico

---

## 1. Pipeline de Carga (Sequência Temporal)

```mermaid
sequenceDiagram
    actor User as 👤 Usuário
    participant UI as 🖥️ Streamlit UI
    participant SVC as 📦 TestReadService
    participant CACHE as 🗄️ TTLCache
    participant REPO as 🗃️ SqlTestQueryRepo
    participant DB as 🏭 SQL Server

    User->>UI: Clica "Carregar ensaio"
    UI->>SVC: load_test(1, "C01_TESTE_001")
    SVC->>CACHE: get("test:1:C01_TESTE_001")
    CACHE-->>SVC: ❌ MISS (cold path)

    Note over SVC,DB: ═══ FASE 1: Metadados ═══

    SVC->>REPO: load_dynamic_rows(ctx)
    REPO->>DB: _get_columns("Cilindro_01")<br/>SELECT TOP 0 * FROM Cilindro_01
    DB-->>REPO: 20 colunas | ⏱️ 525 ms
    REPO->>DB: SELECT * FROM Cilindro_01<br/>WHERE ID_Teste = 'C01_TESTE_001'<br/>ORDER BY LocalCol
    DB-->>REPO: 100 rows | ⏱️ 11.965 ms 🔴

    Note over SVC,DB: ═══ FASE 2: Dados Estáticos ═══

    SVC->>REPO: load_static_row(ctx)
    REPO->>DB: _find_static_table()<br/>sys.tables IN (...) | ⏱️ 88 ms
    REPO->>DB: _get_columns(static) | ⏱️ 249 ms
    REPO->>DB: SELECT * FROM static<br/>WHERE ID_Teste = ? | ⏱️ 356 ms
    DB-->>REPO: 1 row

    Note over SVC,DB: ═══ FASE 3: Metadados Y ═══

    SVC->>REPO: detect_force_column() → cached | ⏱️ 0 ms
    SVC->>REPO: load_available_y_columns() → cached | ⏱️ 0 ms

    SVC->>CACHE: set("test:1:C01_TESTE_001", response)
    SVC-->>UI: LoadTestResponse ✅
    UI->>UI: _plot_multiaxis(df, y_cols)<br/>Plotly render | ⏱️ ~500 ms
    UI-->>User: 📊 Gráfico exibido
```

---

## 2. Distribuição de Tempo por Subsistema

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'pie1': '#f0883e', 'pie2': '#5b9bd5', 'pie3': '#6bbf6b', 'pie4': '#e05555'}}}%%
pie showData
    title Tempo Total: ~14.0 segundos
    "SELECT dynamic (full scan)" : 11965
    "Plotly render" : 500
    "get_columns (metadata)" : 774
    "SELECT static" : 356
    "table_exists / connect" : 370
```

---

## 3. Fluxograma do Problema

```mermaid
flowchart TD
    A["🟢 Usuário clica Carregar"] --> B["📦 load_test() chamado"]
    B --> C{"🗄️ TTLCache hit?"}
    C -->|"Sim ✅ (hot)"| Z["⚡ Retorno < 1ms"]
    C -->|"Não ❌ (cold)"| D["📐 _get_columns()<br/>⏱️ 525 ms"]
    D --> E["🔴 SELECT * FROM Cilindro_01<br/>WHERE ID_Teste = ?<br/>ORDER BY LocalCol<br/>⏱️ 11.965 ms"]
    E --> F{"❓ Por que 12 segundos<br/>para 100 linhas?"}
    F --> G["❌ FULL TABLE SCAN<br/>sem índice em ID_Teste"]
    G --> H["📊 Tabela Cilindro_01<br/>tem milhares/milhões de linhas<br/>varre TODAS para achar 100"]
    H --> I["🛠️ SOLUÇÃO:<br/>CREATE INDEX<br/>IX_Cilindro_01_ID_Teste_LocalCol<br/>ON Cilindro_01(ID_Teste, LocalCol)<br/>INCLUDE (colunas)"]

    style E fill:#e05555,color:#fff,stroke:#a33
    style G fill:#e05555,color:#fff,stroke:#a33
    style H fill:#e05555,color:#fff,stroke:#a33
    style I fill:#6bbf6b,color:#fff,stroke:#3a3
    style Z fill:#6bbf6b,color:#fff,stroke:#3a3
```

---

## 4. Detalhamento por Etapa

### 4.1 Metadados de Colunas (`_get_columns`)

| Chamada | Query | Tempo | Cacheável |
|---------|-------|-------|-----------|
| `_get_columns("Cilindro_01")` | `SELECT TOP 0 * FROM Cilindro_01` | **525 ms** | ✅ Sim (instância) |
| `_get_columns("Cilindro_01_Estático")` | `SELECT TOP 0 * FROM [Cilindro_01_Estático]` | **249 ms** | ✅ Sim (instância) |
| Cache hit (segunda chamada) | — | **0 ms** | — |

> **Nota:** O `TOP 0` no SQL Server obtém apenas os metadados da tabela (schema) sem ler dados. O tempo de ~500ms reflete latência de rede + parsing do schema.

### 4.2 Descoberta de Tabela Estática (`_find_static_table`)

| Chamada | Query | Tempo |
|---------|-------|-------|
| Verificar 4 candidatos | `SELECT name FROM sys.tables WHERE name IN (?,?,?,?)` | **88 ms** |

> **Nota:** Otimização já aplicada — consulta única com `IN` em vez de 4× `SELECT 1 FROM sys.tables`.

### 4.3 🔴 Query Dinâmica — O Gargalo

| Query | Linhas Retornadas | Tempo | % do Total |
|-------|-------------------|-------|------------|
| `SELECT * FROM Cilindro_01 WHERE Cilindro_01_ID_Teste = 'C01_TESTE_001' ORDER BY LocalCol` | 100 | **11.965 ms** | **85.5%** |

#### Por que 12 segundos para 100 linhas?

```mermaid
flowchart LR
    subgraph "Cilindro_01 (sem índice)"
        A["Row 1"] --> B["Row 2"] --> C["..."] --> D["Row N"]
        style A fill:#1a1f24,stroke:#f0883e,color:#ece8de
        style B fill:#1a1f24,stroke:#f0883e,color:#ece8de
        style C fill:#1a1f24,stroke:#f0883e,color:#ece8de
        style D fill:#1a1f24,stroke:#f0883e,color:#ece8de
    end
    E["SQL Server"] -->|"TABLE SCAN: lê TODAS as N linhas"| A
    E -->|"Filtra ID_Teste = 'C01_TESTE_001'"| F["100 linhas ✅"]
    E -->|"Descarta"| G["N-100 linhas ❌"]

    style E fill:#e05555,color:#fff
    style F fill:#6bbf6b,color:#fff
    style G fill:#555,color:#ccc
```

- O SQL Server **varre a tabela inteira** (`Cilindro_01`) linha por linha
- Para cada linha, verifica se `Cilindro_01_ID_Teste = 'C01_TESTE_001'`
- A tabela contém **dezenas/centenas de milhares** de linhas (todos os ensaios de todos os tempos)
- Apenas 100 linhas pertencem ao ensaio `C01_TESTE_001`
- **Sem índice**, o SQL Server não tem como "pular" direto para as linhas do ensaio

### 4.4 Query Estática

| Query | Linhas | Tempo |
|-------|--------|-------|
| `SELECT * FROM [Cilindro_01_Estático] WHERE Cilindro_01_ID_Teste = ?` | 1 | **356 ms** |

> **Nota:** Significativamente mais rápida porque a tabela estática é muito menor (1 linha por ensaio).

---

## 5. Causa Raiz

```mermaid
mindmap
  root((🔴 Lentidão<br/>~14s total))
    SELECT Dynamic
      12 segundos
      85% do tempo
      Full Table Scan
        Sem índice em ID_Teste
        Milhares de linhas na tabela
        Apenas 100 relevantes
    Metadados
      ~800 ms
      5% do tempo
      TOP 0 query
      Cache de instância eficaz
    Conexão ODBC
      ~300 ms
      2% do tempo
      Pool de conexão ativo
    Plotly Render
      ~500 ms
      4% do tempo
      Aceitável para 100 pts
```

---

## 6. Solução

### Índice Ausente (já documentado no projeto)

O script `sql/performance/02_create_composite_indexes.sql` **já existe no workspace** mas **não foi aplicado** ao banco `Projeto_54`. Ele contém:

```sql
CREATE NONCLUSTERED INDEX IX_Cilindro_01_ID_Teste_LocalCol
ON dbo.Cilindro_01 (Cilindro_01_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora,
         Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);
```

### Impacto Estimado

| Cenário | Tempo SELECT Dynamic | Tempo Total | Redução |
|---------|---------------------|-------------|---------|
| **Atual (sem índice)** | 11.965 ms | ~14.0 s | — |
| **Com índice composto** | ~50-200 ms (estimado) | ~1.5 s | **~89%** |

```mermaid
gantt
    title Comparação: Antes vs Depois do Índice
    dateFormat X
    axisFormat %s

    section Antes (sem índice)
    Connect + Metadata    :done, a1, 0, 1000
    SELECT Dynamic 🔴     :crit, a2, 1000, 13000
    SELECT Static         :done, a3, 13000, 13400
    Plotly Render         :done, a4, 13400, 14000

    section Depois (com índice)
    Connect + Metadata    :done, b1, 0, 1000
    SELECT Dynamic 🟢     :active, b2, 1000, 1200
    SELECT Static         :done, b3, 1200, 1600
    Plotly Render         :done, b4, 1600, 2100
```

---

## 7. Recomendações

| # | Ação | Prioridade | Impacto |
|---|------|-----------|---------|
| 1 | Executar `sql/performance/02_create_composite_indexes.sql` no banco `Projeto_54` | 🔴 **Crítica** | 89% de redução |
| 2 | Executar `sql/performance/03_update_stats_and_index_review.sql` para atualizar estatísticas | 🟡 Alta | Otimizador de queries |
| 3 | Após índice, reexecutar `bench.py` para validar melhoria | 🟡 Alta | Confirmação |
| 4 | Hot path (TTLCache) já cobre segundo acesso — manter TTL de 300s | 🟢 OK | Cache hit < 1ms |

---

## 8. Notas Técnicas

- **ODBC Driver:** `ODBC Driver 17 for SQL Server` com conexão Windows Authentication
- **Pool de conexão:** Cada `fetch_all()` abre e fecha uma conexão via `contextmanager`. O ODBC driver mantém pool interno, então o custo é ~280-330ms por nova conexão física (amortizado pelo pool após a primeira)
- **Cache de schema:** `_columns_cache` e `_tables_cache` são dicionários Python na instância do repositório — sobrevivem enquanto o objeto `SqlTestQueryRepository` existir (session_state no Streamlit)
- **Cache de dados:** `TTLCache` com TTL de 300 segundos (5 min) — armazena o `LoadTestResponse` completo em memória
