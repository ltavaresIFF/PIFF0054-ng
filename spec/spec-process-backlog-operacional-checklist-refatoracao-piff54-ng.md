---
title: Backlog Operacional em Checklist - Refatoracao Report_PIFF54 para NG
version: 1.0
date_created: 2026-06-26
last_updated: 2026-06-26
owner: Engenharia de Software - Projeto PIFF54
tags: [process, backlog, checklist, sprint, execution]
---

# Introduction

Checklist operacional para execucao do backlog de refatoracao no Report_PIFF0054-ng. Este artefato e orientado a acompanhamento diario de entrega por sprint e subagente.

## 1. Purpose & Scope

Objetivo:
- converter o plano de sprint em itens executaveis e marcaveis
- facilitar controle de progresso por subagente

Escopo:
- itens BLK das sprints S1, S2, S3 e S4

## 2. Definitions

- [ ]: item pendente.
- [x]: item concluido.
- blocked: item com impedimento externo.

## 3. Requirements, Constraints & Guidelines

- REQ-CHK-001: Todo item concluido deve ter evidencias de implementacao e teste.
- REQ-CHK-002: Itens com dependencia nao podem iniciar antes do predecessor.
- CON-CHK-001: Nao marcar item como concluido sem validar DoD da sprint.
- GUD-CHK-001: Atualizar status ao final de cada bloco de trabalho.

## 4. Interfaces & Data Contracts

Contrato de acompanhamento por item:

| Campo | Regra |
|---|---|
| backlog_id | deve existir no plano de sprint |
| owner_sag | subagente responsavel |
| status | todo, doing, review, done, blocked |
| evidence | link para PR, commit, teste ou relatorio |

## 5. Acceptance Criteria

- AC-CHK-001: Given item marcado done, When revisar evidencia, Then existe codigo e teste correspondente.
- AC-CHK-002: Given sprint encerrada, When auditar checklist, Then nenhum item critico permanece em blocked sem plano.

## 6. Test Automation Strategy

- Validar cada item com ao menos um teste automatizado ou smoke test rastreavel.

## 7. Rationale & Context

Checklist reduz perda de contexto entre subagentes e permite auditoria simples de progresso.

## 8. Dependencies & External Integrations

- Dependencia principal: spec-process-plano-execucao-sprints-refatoracao-piff54-ng.md

## 9. Examples & Edge Cases

```text
Se um item entrar em blocked por dependencia externa,
registrar causa e proximo passo no proprio item antes da daily.
```

## 10. Validation Criteria

- Todo item done deve apontar para evidencia.
- Toda sprint deve registrar data de fechamento.

## 11. Related Specifications / Further Reading

- spec-process-plano-execucao-sprints-refatoracao-piff54-ng.md
- spec-architecture-refatoracao-report-piff54-ng.md

## 12. Checklist por Sprint

### Sprint S1 - Fundacao

- [ ] BLK-S1-ARCH-01 - Criar estrutura de pastas em camadas (ui/application/domain/infrastructure/tests).
  - owner: SAG-INT
  - status: todo
  - dependencies: nenhuma
  - evidence:

- [ ] BLK-S1-CONTRACT-01 - Formalizar contratos de contexto de ensaio e observacao.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S1-ARCH-01
  - evidence:

- [ ] BLK-S1-DB-01 - Consolidar mapa de tabelas e colunas para cilindros 01-06.
  - owner: SAG-DB
  - status: todo
  - dependencies: BLK-S1-CONTRACT-01
  - evidence:

- [ ] BLK-S1-CI-01 - Configurar pipeline basico com lint + unit tests.
  - owner: SAG-INT
  - status: todo
  - dependencies: BLK-S1-ARCH-01
  - evidence:

### Sprint S2 - Core de Leitura e Observacao

- [ ] BLK-S2-READ-01 - Implementar listagem de ID_Teste por cilindro com fallback dinamico->estatico.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S1-CONTRACT-01
  - evidence:

- [ ] BLK-S2-READ-02 - Implementar carga dinamica ordenada por LocalCol.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S2-READ-01
  - evidence:

- [ ] BLK-S2-READ-03 - Implementar carga estatica com fallback de nome de tabela.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S2-READ-01
  - evidence:

- [ ] BLK-S2-OBS-01 - Implementar upsert de OBS, val_obs e y_column_name com rowcount=1.
  - owner: SAG-DB
  - status: todo
  - dependencies: BLK-S1-DB-01
  - evidence:

- [ ] BLK-S2-OBS-02 - Implementar leitura e remocao de observacao por coordenada.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S2-OBS-01
  - evidence:

- [ ] BLK-S2-TST-01 - Cobrir cenarios de sucesso, zero-match e multi-match.
  - owner: SAG-QA
  - status: todo
  - dependencies: BLK-S2-READ-02, BLK-S2-OBS-01
  - evidence:

### Sprint S3 - UX e Exportacoes

- [ ] BLK-S3-UI-01 - Implementar selecao de variaveis Y e grafico com multiplos eixos.
  - owner: SAG-FE
  - status: todo
  - dependencies: BLK-S2-READ-02
  - evidence:

- [ ] BLK-S3-UI-02 - Implementar editor de observacao conectado ao ponto selecionado.
  - owner: SAG-FE
  - status: todo
  - dependencies: BLK-S2-OBS-01, BLK-S2-OBS-02
  - evidence:

- [ ] BLK-S3-UI-03 - Aplicar token system, tipografia e assinatura visual de dominio.
  - owner: SAG-FE
  - status: todo
  - dependencies: BLK-S3-UI-01
  - evidence:

- [ ] BLK-S3-CSV-01 - Implementar exportacao CSV com separador ';'.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S2-READ-02
  - evidence:

- [ ] BLK-S3-PDF-01 - Implementar pipeline PDF em modos config_atual e todos_valores.
  - owner: SAG-REPORT
  - status: todo
  - dependencies: BLK-S2-READ-02
  - evidence:

- [ ] BLK-S3-A11Y-01 - Validar responsividade, foco de teclado e reduced motion.
  - owner: SAG-QA
  - status: todo
  - dependencies: BLK-S3-UI-03
  - evidence:

### Sprint S4 - Endurecimento e Release

- [ ] BLK-S4-PERF-01A - Executar baseline de tempos e IO para DISTINCT ID_Teste e carga por ID_Teste (recorte 01-06).
  - owner: SAG-DB
  - status: todo
  - dependencies: BLK-S2-READ-02
  - evidence:

- [ ] BLK-S4-PERF-01B - Aplicar indices compostos (ID_Teste, LocalCol) nas tabelas dinamicas do recorte 01-06.
  - owner: SAG-DB
  - status: todo
  - dependencies: BLK-S4-PERF-01A
  - evidence:

- [ ] BLK-S4-PERF-01C - Revisar indices redundantes e atualizar estatisticas (EXEC sp_updatestats).
  - owner: SAG-DB
  - status: todo
  - dependencies: BLK-S4-PERF-01B
  - evidence:

- [ ] BLK-S4-PERF-01D - Remover SELECT * das consultas estaticas e validar benchmark antes/depois.
  - owner: SAG-BE
  - status: todo
  - dependencies: BLK-S4-PERF-01C, BLK-S3-PDF-01
  - evidence:

- [ ] BLK-S4-REG-01 - Rodar regressao completa versus baseline funcional.
  - owner: SAG-QA
  - status: todo
  - dependencies: BLK-S3-A11Y-01, BLK-S4-PERF-01D
  - evidence:

- [ ] BLK-S4-DOC-01 - Consolidar documentacao operacional e tecnica.
  - owner: SAG-INT
  - status: todo
  - dependencies: BLK-S4-REG-01
  - evidence:

- [ ] BLK-S4-REL-01 - Preparar release candidate com checklist de rollback.
  - owner: SAG-INT
  - status: todo
  - dependencies: BLK-S4-REG-01, BLK-S4-DOC-01
  - evidence:
