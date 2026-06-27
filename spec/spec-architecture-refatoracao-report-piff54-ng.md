---
title: Especificacao Tecnica de Refatoracao do Report_PIFF54 para Report_PIFF0054-ng
version: 1.0
date_created: 2026-06-26
last_updated: 2026-06-26
owner: Engenharia de Software - Projeto PIFF54
tags: [architecture, process, design, data, refactor, ai-ready]
---

# Introduction

Esta especificacao define requisitos, restricoes, contratos e criterios de validacao para refatorar o sistema implementado em Report_PIFF54 para um novo projeto em Report_PIFF0054-ng. O documento foi escrito para consumo por agentes de IA que atuarao em subagentes especializados.

## 1. Purpose & Scope

Objetivo:
- Especificar, de forma executavel por IA, como reproduzir e evoluir as capacidades atuais do sistema Report_PIFF54 no novo projeto Report_PIFF0054-ng.

Escopo funcional alvo:
- Consulta de ensaios por cilindro e ID_Teste em SQL Server.
- Visualizacao de series temporais com multiplos eixos Y.
- Persistencia read-write de observacoes por coordenada (LocalCol + serie + valor).
- Exportacao de relatorio PDF tecnico e exportacao CSV.
- Cache, diagnostico operacional e tratamento de erro amigavel.

Escopo arquitetural alvo:
- Modularizacao clara entre UI, dominio/aplicacao, infraestrutura de dados e exportadores.
- Contratos estaveis para repositorios e servicos.
- Preparacao para testes unitarios, integracao e e2e.

Fora de escopo desta versao:
- Migracao completa de dados legados Access (.mdb/.accdb).
- Reescrita do schema SQL alem do recorte estabilizado (cilindros 01 a 06 como baseline confiavel).

Publico alvo:
- Agentes de IA implementadores (subagentes).
- Desenvolvedores humanos revisores.
- Responsaveis por homologacao tecnica.

Premissas:
- Banco SQL Server disponivel e acessivel.
- Projeto fonte Report_PIFF54 permanece como referencia comportamental.
- Novo projeto sera mantido em Report_PIFF0054-ng.

## 2. Definitions

- AC: Acceptance Criteria.
- DAL: Data Access Layer.
- DTO: Data Transfer Object.
- ID_Teste: identificador de ensaio por cilindro.
- LocalCol: coluna temporal/sequencial usada como eixo X.
- OBS: coluna de comentario tecnico por coordenada.
- val_obs: coluna de valor numerico associado a observacao.
- y_column_name: coluna com o nome da variavel tecnica observada.
- UI: User Interface.
- BFF: Backend-for-Frontend (camada de orquestracao para UI).
- RF: Requisito Funcional.
- RNF: Requisito Nao Funcional.
- CON: Restricao obrigatoria.
- GUD: Guia recomendado.
- PAT: Padrao de implementacao.

## 3. Requirements, Constraints & Guidelines

### 3.1 Requisitos funcionais

- REQ-001: O sistema deve listar cilindros configurados e carregar IDs de teste por cilindro com fallback dinamico->estatico.
- REQ-002: O sistema deve carregar dados dinamicos por ID_Teste com ordenacao deterministica por LocalCol.
- REQ-003: O sistema deve carregar registro estatico por ID_Teste com tolerancia para variacoes de nomenclatura de tabela estatica.
- REQ-004: O sistema deve detectar coluna de forca automaticamente (padrao principal e fallback).
- REQ-005: O sistema deve permitir selecao de multiplas variaveis Y para visualizacao simultanea.
- REQ-006: O sistema deve renderizar grafico interativo com multiplos eixos Y independentes.
- REQ-007: O sistema deve suportar selecao de ponto no grafico e abrir fluxo de observacao por coordenada.
- REQ-008: O sistema deve persistir observacao de forma atomica nas colunas canonicamente definidas: OBS, val_obs, y_column_name.
- REQ-009: O sistema deve recuperar observacao existente do ponto selecionado para pre-carga no editor.
- REQ-010: O sistema deve permitir excluir observacao por coordenada com validacao de unicidade da linha alvo.
- REQ-011: O sistema deve exportar CSV com compatibilidade para Excel regional PT-BR (separador ';').
- REQ-012: O sistema deve exportar PDF tecnico no layout industrial com metadados de teste, grafico e tabela resumida.
- REQ-013: O sistema deve suportar dois modos de exportacao de grafico no PDF: espelhar contexto atual e intervalo completo.
- REQ-014: O sistema deve exibir diagnostico operacional (drivers, conexao, contexto ativo).
- REQ-015: O sistema deve apresentar erros de negocio e infraestrutura em mensagens amigaveis ao operador.

### 3.2 Requisitos nao funcionais

- NFR-001: Latencia de leitura de dados por teste deve ser adequada para uso interativo com cache de curta duracao.
- NFR-002: Operacoes de escrita de observacao devem validar rowcount=1 e executar rollback em falha.
- NFR-003: Consultas devem usar parametros posicionais para valores dinamicos.
- NFR-004: Identificadores SQL dinamicos devem ser escapados com seguranca.
- NFR-005: O sistema deve manter compatibilidade de comportamento com o sistema atual para o recorte validado.
- NFR-006: O projeto deve permitir cobertura de testes automatizados para logica critica de dominio e exportacao.
- NFR-007: O frontend deve ser responsivo para desktop e mobile, com foco visivel de teclado e suporte a reduced motion.
- NFR-008: O backend deve implementar o pacote minimo de performance SQL para o recorte 01-06: indice composto por ID_Teste + LocalCol, revisao de redundancia de indices, atualizacao de estatisticas e benchmark antes/depois.
- NFR-009: Consultas de leitura estatica nao devem usar SELECT *; devem usar lista explicita de colunas.

### 3.3 Restricoes obrigatorias

- CON-001: A implementacao nova deve residir em Report_PIFF0054-ng.
- CON-002: A especificacao tecnica deve residir em Report_PIFF0054-ng/spec.
- CON-003: O recorte de confiabilidade inicial para engenharia reversa e otimizado para cilindros 01 a 06.
- CON-004: Colunas canonicas de observacao para escrita: OBS, val_obs, y_column_name.
- CON-005: Fluxos que possam alterar dados devem ser explicitamente transacionais.
- CON-006: Nao usar concatenacao direta de input do usuario em SQL.

### 3.4 Guidelines de implementacao

- GUD-001: Separar projeto por camadas: ui, application, domain, infrastructure, tests.
- GUD-002: Extrair contratos de repositorio antes de implementar adaptadores concretos SQL.
- GUD-003: Preservar semantica funcional do sistema atual antes de evolucoes visuais/arquiteturais.
- GUD-004: Adotar nomenclatura estavel e orientada a casos de uso (nao orientada ao framework).
- GUD-005: Centralizar constantes de schema/colunas para reduzir drift entre modulos.
- GUD-006: Criar fixtures de dados para testes reproduziveis por cilindro e tipo de ensaio.

### 3.5 Padroes arquiteturais

- PAT-001: Ports and Adapters para desacoplar UI e banco.
- PAT-002: Use Case orientado a comandos/consultas (query services para leitura, command services para escrita).
- PAT-003: DTOs versionados para contratos de exportacao e visualizacao.
- PAT-004: Validacao de input centralizada na camada application.
- PAT-005: Erros tipados de dominio com mapeamento para mensagens de UI.

### 3.6 Requisitos de design frontend (frontend-design skill aplicada)

Direcao visual obrigatoria para o novo frontend:
- DSG-001: Assunto visual: "painel tecnico de ensaios industriais" para operadores de processo; job principal da pagina: "detectar anomalia e registrar evidencia rapidamente".
- DSG-002: Definir token system explicito com 4-6 cores nomeadas e papeis semanticos (bg, surface, accent, danger, data-highlight).
- DSG-003: Definir 3 papeis tipograficos (display, body, mono/utilitaria) com escala de tamanho clara.
- DSG-004: Ter 1 elemento de assinatura visual memoravel ligado ao dominio (ex.: trilha temporal industrial com marcadores de eventos).
- DSG-005: Evitar layout generico de dashboard; estrutura deve refletir fluxo real de operacao (selecao > leitura > anotacao > evidencia).
- DSG-006: Animacao deve ser deliberada e comedida: entrada de contexto e destaque de ponto observado.
- DSG-007: O frontend deve implementar estados vazios, erro e sem dados com texto acionavel.

## 4. Interfaces & Data Contracts

### 4.1 Contexto de ensaio

```json
{
  "db_name": "Projeto_54",
  "cyl_num": 1,
  "table_dynamic": "Cilindro_01",
  "table_static": "Cilindro_01_Estatico",
  "test_id": "TESTE_2026_0001"
}
```

### 4.2 Contrato de leitura de serie dinamica

```json
{
  "rows": [
    {
      "LocalCol": "2026-05-10 10:00:01",
      "Forca": 123.45,
      "Pressao_Compressor": 10.1,
      "Pressao_Reguladora": 8.8,
      "Temperatura_Ambiente": 27.4,
      "Cilindro_01_ID_Teste": "TESTE_2026_0001"
    }
  ],
  "meta": {
    "ordered_by": "LocalCol",
    "total_rows": 2500
  }
}
```

### 4.3 Contrato de observacao por coordenada

Entrada (command):

```json
{
  "table": "Cilindro_01",
  "cyl_num": 1,
  "test_id": "TESTE_2026_0001",
  "local_col": "2026-05-10 10:02:15",
  "y_column_name": "Forca",
  "y_value": 333.12,
  "obs_text": "Pico abrupto apos troca de carga"
}
```

Saida (result):

```json
{
  "updated": true,
  "matched_rows": 1,
  "columns_used": {
    "obs": "OBS",
    "val": "val_obs",
    "y_name": "y_column_name"
  }
}
```

### 4.4 Contrato de exportacao PDF

```json
{
  "meta": {
    "cliente": "Cliente X",
    "cyl_label": "Cilindro 01",
    "test_id": "TESTE_2026_0001",
    "tipo_carga": "P1",
    "export_mode": "config_atual"
  },
  "graph_png": "bytes",
  "table_sample_max_rows": 500,
  "observations": []
}
```

### 4.5 Contrato de modulo (interfaces sugeridas)

```python
class TestQueryRepository(Protocol):
    def list_test_ids(self, ctx: TestContext) -> list[str]: ...
    def load_dynamic_rows(self, ctx: TestContext, selected_columns: list[str] | None = None) -> pd.DataFrame: ...
    def load_static_row(self, ctx: TestContext) -> pd.DataFrame: ...

class ObservationCommandRepository(Protocol):
    def upsert_observation(self, cmd: ObservationCommand) -> ObservationResult: ...
    def get_observation(self, cmd: ObservationLookup) -> ObservationRecord | None: ...
    def delete_observation(self, cmd: ObservationLookup) -> bool: ...
```

## 5. Acceptance Criteria

- AC-001: Given cilindro valido e banco acessivel, When operador seleciona cilindro, Then a lista de ID_Teste e carregada e ordenada.
- AC-002: Given ID_Teste selecionado, When operador solicita dados, Then o sistema retorna linhas dinamicas ordenadas por LocalCol.
- AC-003: Given ponto selecionado no grafico, When operador grava comentario valido, Then apenas 1 linha e atualizada com OBS, val_obs e y_column_name.
- AC-004: Given observacao existente no mesmo ponto, When operador reabre editor, Then comentario e pre-carregado corretamente.
- AC-005: Given operacao de escrita sem match unico, When tentativa de gravacao ocorre, Then o sistema falha com erro amigavel e sem escrita parcial.
- AC-006: Given dados carregados, When operador exporta PDF, Then o arquivo contem cabecalho, metadados, grafico e tabela conforme contrato.
- AC-007: Given modo PDF "todos_valores", When exportacao ocorre, Then a janela temporal nao deve ser limitada pelo filtro visual atual.
- AC-008: Given frontend em viewport mobile, When usuario navega fluxo principal, Then todas as acoes criticas permanecem acessiveis e legiveis.
- AC-009: Given pipeline de testes, When suite principal executa, Then testes de logica critica passam sem regressao de comportamento.

## 6. Test Automation Strategy

- Test Levels: Unit, Integration, End-to-End.
- Frameworks: pytest, unittest (compat), Playwright ou equivalente para fluxos de UI quando aplicavel.
- Test Data Management: fixtures SQL com seeds deterministicas para cilindros 01-06 e cenarios de observacao (match unico, zero match, multi-match).
- CI/CD Integration: pipeline com gates para lint, type-check, unit e integration smoke.
- Coverage Requirements: minimo 80% em camada application/domain, 70% em infraestrutura critica e 70% no frontend critico.
- Performance Testing: cenarios de carga de leitura para 2500 linhas por ensaio e medicao de tempo de resposta de consultas chave.

Matriz minima de testes por requisito:
- TST-REQ-001: listagem de IDs por cilindro.
- TST-REQ-002: carregamento de dinamica ordenada.
- TST-REQ-008: upsert de observacao com transacao.
- TST-REQ-010: exclusao de observacao por coordenada.
- TST-REQ-012: composicao PDF com secoes obrigatorias.
- TST-DSG-005: fluxo UX principal sem bloqueio em mobile.
- TST-PERF-001: benchmark DISTINCT ID_Teste e carga dinamica por ID_Teste antes/depois dos indices compostos.
- TST-PERF-002: validacao de plano de execucao apos remocao de SELECT * na carga estatica.
- TST-PERF-003: validacao de melhoria ou nao-regressao apos EXEC sp_updatestats.

## 7. Rationale & Context

Racional tecnico:
- O sistema atual concentra logica relevante em Streamlit + modulos utilitarios; a refatoracao precisa separar responsabilidades para facilitar manutencao e automacao por IA.
- O recorte 01-06 e o baseline mais estavel para iniciar evolucao sem propagar inconsistencias de schema presentes fora do recorte.
- A feature de observacao por coordenada e critica para valor operacional e exige contrato estrito para integridade.

Racional de design:
- O frontend atual e funcional, mas pode evoluir para uma linguagem visual mais intencional e menos generica.
- A direcao "painel tecnico de ensaios industriais" conecta estetica e usabilidade ao contexto real de operadores.

## 8. Dependencies & External Integrations

### External Systems
- EXT-001: SQL Server (Projeto_54) - fonte primaria de dados dinamicos e estaticos.

### Third-Party Services
- SVC-001: N/A - operacao local sem dependencia obrigatoria de servicos SaaS.

### Infrastructure Dependencies
- INF-001: Ambiente Windows com driver ODBC SQL Server funcional.
- INF-002: Runtime Python com suporte as bibliotecas de dados e visualizacao.

### Data Dependencies
- DAT-001: Tabelas Cilindro_01..06 e Cilindro_01_Estatico..06_Estatico como baseline.
- DAT-002: Colunas LocalCol, ID_Teste, OBS, val_obs, y_column_name disponiveis ou criaveis de forma idempotente.

### Technology Platform Dependencies
- PLT-001: Streamlit para UI atual de referencia comportamental.
- PLT-002: Plotly para visualizacao interativa e serializacao para imagem de exportacao.
- PLT-003: Mecanismo de geracao de PDF com composicao de layout tecnico.

### Compliance Dependencies
- COM-001: Rastreabilidade tecnica de observacoes por ponto de ensaio para auditoria interna.

## 9. Examples & Edge Cases

Exemplo de fluxo de gravacao com sucesso:

```text
Input:
- test_id=TESTE_2026_0001
- local_col=2026-05-10 10:02:15
- y_column_name=Forca
- y_value=333.12
- obs_text="Pico apos troca de carga"

Output esperado:
- updated=true
- matched_rows=1
```

Edge cases obrigatorios:
- EDGE-001: LocalCol inexistente para o test_id -> falha amigavel sem escrita.
- EDGE-002: Valor Y com mais de um match dentro da tolerancia -> falha por ambiguidade.
- EDGE-003: obs_text vazio apos trim -> persistir NULL.
- EDGE-004: obs_text maior que limite -> rejeitar com validacao.
- EDGE-005: tabela estatica com nome alternativo (acento/sem acento) -> fallback automatico.
- EDGE-006: modo PDF intervalo completo ignorando range visual -> exportacao sem corte temporal.

## 10. Validation Criteria

- VAL-001: Todos os ACs desta especificacao devem ter teste automatizado correspondente.
- VAL-002: Validacao manual deve confirmar paridade funcional com fluxos criticos do Report_PIFF54.
- VAL-003: Operacoes de observacao devem demonstrar atomicidade (commit/rollback) em testes de falha.
- VAL-004: Analise estatica/lint sem erros bloqueantes nas camadas novas.
- VAL-005: Checklist de UX responsiva e acessibilidade minima aprovado.
- VAL-006: Benchmark de consultas principais documentado antes/depois da refatoracao.

## 11. Related Specifications / Further Reading

- ../docs/ENGENHARIA_REVERSA_SQL_PROJETO_54.md
- ../../Report_PIFF54/Docs/Requisitos_Visualizador_MDB.md
- ../../Report_PIFF54/FEATURE_OBSERVACOES_IMPLEMENTACAO.md
- ../../Report_PIFF54/FEATURE_OBSERVACOES_POR_COORDENADA.md

## Anexo A - Plano de execucao por subagentes

Subagentes sugeridos (execucao paralela quando possivel):

1. Subagente Schema-Reverse-Guard
- Objetivo: consolidar contratos SQL do recorte 01-06 e detectar drift de schema.
- Entregas: schema_contracts.md, checklist de constraints/indices, scripts idempotentes.

2. Subagente Backend-UseCases
- Objetivo: implementar camada application/domain (casos de uso de leitura, observacao e exportacao).
- Entregas: contratos de repositorio, servicos, validadores, erros tipados, testes unitarios.

3. Subagente Infra-SQL-Adapter
- Objetivo: implementar adaptador SQL seguro com queries parametrizadas e transacoes de observacao.
- Entregas: repositorios concretos, mapeadores DataFrame/DTO, testes de integracao.

4. Subagente Frontend-Experience (frontend-design)
- Objetivo: redesenhar frontend com direcao visual distinta e orientada ao fluxo operacional.
- Entregas:
  - token-system.md com paleta e papeis semanticos
  - typographic-scale.md com papeis display/body/mono
  - ui-flow.md com wireframes desktop/mobile
  - implementacao da assinatura visual unica no fluxo de anotacao por coordenada
- Restricoes: nao usar layout generico; garantir acessibilidade e reduced motion.

5. Subagente Reporting-PDF
- Objetivo: refatorar pipeline de PDF com contratos estaveis e regressao zero no conteudo tecnico.
- Entregas: engine_pdf, testes de snapshot estrutural e validacao de metadados.

6. Subagente QA-Homologacao
- Objetivo: consolidar matriz de testes e executar homologacao funcional do recorte.
- Entregas: relatorio de conformidade AC/VAL, riscos residuais, plano de correcoes.

Ordem recomendada:
1) Schema-Reverse-Guard
2) Backend-UseCases + Infra-SQL-Adapter
3) Frontend-Experience + Reporting-PDF
4) QA-Homologacao
