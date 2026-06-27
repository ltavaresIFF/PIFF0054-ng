---
title: Plano de Execucao por Sprint - Refatoracao Report_PIFF54 para Report_PIFF0054-ng
version: 1.0
date_created: 2026-06-26
last_updated: 2026-06-26
owner: Engenharia de Software - Projeto PIFF54
tags: [process, architecture, backlog, sprints, refatoracao, ai-agents]
---

# Introduction

Este documento define o plano de execucao por sprint para a refatoracao do sistema Report_PIFF54 no novo projeto Report_PIFF0054-ng. O plano foi otimizado para uso por agentes de IA em paralelo, com entregas verificaveis e criterios de aceite claros.

## 1. Purpose & Scope

Objetivo:
- transformar a especificacao tecnica em um backlog executavel por sprint
- reduzir risco de regressao funcional durante a migracao
- coordenar subagentes com fronteiras de responsabilidade

Escopo:
- arquitetura, dados, frontend, exportacao, testes e release
- foco inicial no recorte confiavel de cilindros 01 a 06

## 2. Definitions

- Sprint: iteracao time-boxed com objetivo e entregue verificavel.
- DoR: Definition of Ready.
- DoD: Definition of Done.
- SAG: subagente de implementacao especializado.
- Baseline: comportamento atual aceito no sistema fonte.

## 3. Requirements, Constraints & Guidelines

- REQ-PRC-001: Cada sprint deve produzir artefatos validaveis por teste.
- REQ-PRC-002: Cada item de backlog deve mapear para requisitos da especificacao tecnica.
- REQ-PRC-003: Integracao entre subagentes deve ocorrer por contratos versionados.
- CON-PRC-001: Nao iniciar implementacao sem contrato de dados acordado para o item.
- CON-PRC-002: Nao fechar sprint sem evidencia de testes automatizados.
- GUD-PRC-001: Priorizar riscos estruturais cedo (dados, transacao, contratos).
- GUD-PRC-002: Frontend visual deve evoluir apos estabilizacao do nucleo funcional.
- PAT-PRC-001: Fluxo por sprint deve seguir ordem: contratos -> implementacao -> testes -> integracao.

## 4. Interfaces & Data Contracts

Contratos de rastreabilidade do backlog:

| Campo | Descricao |
|---|---|
| backlog_id | identificador unico do item |
| sprint_id | sprint de destino |
| spec_refs | requisitos relacionados na especificacao principal |
| owner_sag | subagente responsavel |
| dependencies | itens predecessores |
| test_refs | testes obrigatorios |
| status | todo, doing, review, done |

Exemplo:

```json
{
  "backlog_id": "BLK-S2-OBS-01",
  "sprint_id": "S2",
  "spec_refs": ["REQ-008", "NFR-002", "SEC-004"],
  "owner_sag": "SAG-DB",
  "dependencies": ["BLK-S1-CONTRACT-01"],
  "test_refs": ["TST-REQ-008", "TST-REQ-010"],
  "status": "todo"
}
```

## 5. Acceptance Criteria

- AC-PRC-001: Given plano de sprint aprovado, When um item e concluido, Then ele possui codigo, teste e evidencia de execucao.
- AC-PRC-002: Given sprint encerrada, When revisar itens done, Then todos possuem mapeamento para requisitos da especificacao tecnica.
- AC-PRC-003: Given integracao de multiplos subagentes, When pipeline roda, Then build e testes criticos passam.
- AC-PRC-004: Given backlog de frontend, When sprint visual fecha, Then criterios de responsividade e acessibilidade minima estao aprovados.

## 6. Test Automation Strategy

- Test Levels: unit, integration, e2e, smoke.
- Frameworks: pytest, unittest compat, Playwright (ou equivalente) para fluxo UI.
- CI/CD Integration: gate obrigatorio para lint, testes, cobertura minima e relatorio.
- Coverage Requirements: 80% application/domain, 70% infraestrutura critica, 70% frontend critico.

## 7. Rationale & Context

O plano prioriza primeiro o risco estrutural (contratos de dados e transacao), depois a migracao de casos de uso, e por fim refinamento de experiencia visual. Isso reduz retrabalho e evita regressao no fluxo de observacoes por coordenada.

## 8. Dependencies & External Integrations

### External Systems
- EXT-PRC-001: SQL Server Projeto_54 para testes de integracao.

### Infrastructure Dependencies
- INF-PRC-001: Ambiente Windows com ODBC funcional.
- INF-PRC-002: Pipeline CI para validacao continua.

### Data Dependencies
- DAT-PRC-001: Recorte cilindros 01-06 como baseline.

### Technology Platform Dependencies
- PLT-PRC-001: stack Python, Streamlit (ou UI alvo), plotagem interativa e engine PDF.

## 9. Examples & Edge Cases

```text
Edge case de processo:
- Item finalizado sem teste automatizado.
Tratamento:
- Item volta para status doing e sprint nao pode ser encerrada ate cumprir DoD.
```

## 10. Validation Criteria

- VAL-PRC-001: Todos os itens sprint possuem rastreabilidade completa (spec -> backlog -> teste).
- VAL-PRC-002: Nenhuma sprint e fechada com bug critico aberto no fluxo principal.
- VAL-PRC-003: Relatorio de sprint contem riscos residuais e plano de mitigacao.

## 11. Related Specifications / Further Reading

- spec-architecture-refatoracao-report-piff54-ng.md
- ../docs/ENGENHARIA_REVERSA_SQL_PROJETO_54.md

## 12. Sprint Plan and Backlog

### Sprint S1 - Fundacao de Contratos e Estrutura

Objetivo:
- estabelecer base arquitetural, contratos de dados e estrutura de projeto

Subagentes:
- SAG-DB
- SAG-BE
- SAG-INT

Backlog:
- BLK-S1-ARCH-01: Criar estrutura de pastas em camadas (ui/application/domain/infrastructure/tests).
- BLK-S1-CONTRACT-01: Formalizar contratos de contexto de ensaio e observacao.
- BLK-S1-DB-01: Consolidar mapa de tabelas e colunas para cilindros 01-06.
- BLK-S1-CI-01: Configurar pipeline basico com lint + unit tests.

DoR:
- especificacao principal aprovada
- ambiente local funcional

DoD:
- contratos versionados
- pipeline executando
- testes iniciais verdes

### Sprint S2 - Casos de Uso Core (Leitura e Observacao)

Objetivo:
- migrar leitura de ensaio e fluxo de observacao por coordenada com integridade transacional

Subagentes:
- SAG-BE
- SAG-DB
- SAG-QA

Backlog:
- BLK-S2-READ-01: Implementar listagem de ID_Teste por cilindro com fallback dinamico->estatico.
- BLK-S2-READ-02: Implementar carga dinamica ordenada por LocalCol.
- BLK-S2-READ-03: Implementar carga estatica com fallback de nome de tabela.
- BLK-S2-OBS-01: Implementar upsert de OBS, val_obs e y_column_name com rowcount=1.
- BLK-S2-OBS-02: Implementar leitura e remocao de observacao por coordenada.
- BLK-S2-TST-01: Cobrir cenarios de sucesso, zero-match e multi-match.

DoD:
- casos de uso core funcionando com testes de integracao
- erros amigaveis mapeados

### Sprint S3 - Visualizacao, UX Operacional e Exportacoes

Objetivo:
- entregar fluxo completo de operacao com identidade visual definida e exportacoes estaveis

Subagentes:
- SAG-FE
- SAG-REPORT
- SAG-QA

Backlog:
- BLK-S3-UI-01: Implementar selecao de variaveis Y e grafico com multiplos eixos.
- BLK-S3-UI-02: Implementar editor de observacao conectado ao ponto selecionado.
- BLK-S3-UI-03: Aplicar token system, tipografia e assinatura visual de dominio.
- BLK-S3-CSV-01: Implementar exportacao CSV com separador ';'.
- BLK-S3-PDF-01: Implementar pipeline PDF em modos config_atual e todos_valores.
- BLK-S3-A11Y-01: Validar responsividade, foco de teclado e reduced motion.

DoD:
- fluxo ponta a ponta operacional
- exportacoes validas
- checklist de UX aprovado

### Sprint S4 - Endurecimento, Performance e Release

Objetivo:
- estabilizar qualidade, performance e empacotar release inicial do NG

Subagentes:
- SAG-QA
- SAG-INT
- SAG-DB

Backlog:
- BLK-S4-PERF-01A: Executar baseline de tempos e IO para DISTINCT ID_Teste e carga por ID_Teste (recorte 01-06).
- BLK-S4-PERF-01B: Aplicar indices compostos (ID_Teste, LocalCol) nas tabelas dinamicas do recorte 01-06.
- BLK-S4-PERF-01C: Revisar indices redundantes e atualizar estatisticas (EXEC sp_updatestats).
- BLK-S4-PERF-01D: Remover SELECT * das consultas estaticas e validar benchmark antes/depois.
- BLK-S4-REG-01: Rodar regressao completa versus baseline funcional.
- BLK-S4-DOC-01: Consolidar documentacao operacional e tecnica.
- BLK-S4-REL-01: Preparar release candidate com checklist de rollback.

DoD:
- suite de testes critica verde
- relatorio de performance aceito
- release candidate aprovado

## 13. Subagent Allocation Matrix

| Subagente | Responsabilidade principal | Sprints |
|---|---|---|
| SAG-DB | contratos SQL, consistencia de schema, migracoes idempotentes | S1, S2, S4 |
| SAG-BE | casos de uso core, validacao e erros de dominio | S1, S2 |
| SAG-FE | UX operacional, identidade visual, fluxo de observacao | S3 |
| SAG-REPORT | exportacao PDF e contratos de relatorio | S3 |
| SAG-QA | matriz de testes, regressao, homologacao | S2, S3, S4 |
| SAG-INT | CI/CD, integracao de entregas, release | S1, S4 |

## 14. Risks and Mitigation

- RSK-001: drift de schema fora do recorte 01-06.
  - MIT-001: feature flags e validacao de contrato por cilindro.
- RSK-002: regressao no fluxo de observacao por coordenada.
  - MIT-002: testes de integracao obrigatorios e bloqueio de merge sem cobertura.
- RSK-003: acoplamento excessivo entre UI e acesso a dados.
  - MIT-003: enforce de interfaces na camada application.
- RSK-004: degradacao visual em mobile.
  - MIT-004: validacao de breakpoints em cada historia de UI.
