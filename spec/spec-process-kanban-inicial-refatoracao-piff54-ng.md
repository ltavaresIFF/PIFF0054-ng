---
title: Kanban Inicial - Refatoracao Report_PIFF54 para Report_PIFF0054-ng
version: 1.0
date_created: 2026-06-26
last_updated: 2026-06-26
owner: Engenharia de Software - Projeto PIFF54
tags: [process, kanban, execution, tracking, ai-agents]
---

# Introduction

Quadro kanban inicial para acompanhamento dos itens BLK da refatoracao. Este documento deve ser atualizado continuamente durante a execucao das sprints.

## 1. Purpose & Scope

Objetivo:
- disponibilizar visao unica e rapida do status de implementacao
- facilitar coordenacao entre subagentes

Escopo:
- itens BLK definidos no plano de execucao por sprint

## 2. Definitions

- To do: item pronto para iniciar.
- Doing: item em andamento.
- Review: item implementado aguardando revisao/QA.
- Done: item aprovado com evidencia.
- Blocked: item impedido por dependencia externa.

## 3. Requirements, Constraints & Guidelines

- REQ-KBN-001: Todo card deve ter owner e sprint.
- REQ-KBN-002: Mudanca de status deve registrar data.
- CON-KBN-001: Item nao pode ir para Done sem evidencia.
- GUD-KBN-001: Manter WIP baixo em Doing por subagente.

## 4. Interfaces & Data Contracts

Contrato minimo de card:

| Campo | Obrigatorio |
|---|---|
| backlog_id | sim |
| sprint_id | sim |
| owner_sag | sim |
| status | sim |
| updated_at | sim |
| evidence | recomendado |

## 5. Acceptance Criteria

- AC-KBN-001: Given item em Done, When auditar card, Then existe evidencia valida.
- AC-KBN-002: Given item em Blocked, When revisar quadro, Then causa e proximo passo estao preenchidos.

## 6. Test Automation Strategy

- Validacao semanal do kanban contra checklist operacional para detectar divergencia de status.

## 7. Rationale & Context

Kanban reduz filas ocultas e melhora previsibilidade de entrega ao tornar gargalos explicitamente visiveis.

## 8. Dependencies & External Integrations

- Dependencia principal: spec-process-plano-execucao-sprints-refatoracao-piff54-ng.md
- Dependencia de apoio: spec-process-backlog-operacional-checklist-refatoracao-piff54-ng.md

## 9. Examples & Edge Cases

```text
Edge case: item marcado como done no kanban e pendente no checklist.
Acao: reconciliar status e manter fonte unica no checklist para auditoria.
```

## 10. Validation Criteria

- Atualizacao de quadro em toda daily.
- Nenhum card sem owner_sag.
- Nenhum card em Review por mais de 3 dias uteis sem decisao.

## 11. Related Specifications / Further Reading

- spec-process-plano-execucao-sprints-refatoracao-piff54-ng.md
- spec-process-backlog-operacional-checklist-refatoracao-piff54-ng.md

## 12. Kanban Board Snapshot

Ultima atualizacao: 2026-06-26

### To do

| backlog_id | sprint | owner_sag | prioridade | dependencies | updated_at | notes |
|---|---|---|---|---|---|---|
| BLK-S1-ARCH-01 | S1 | SAG-INT | alta | - | 2026-06-26 | estrutura de pastas |
| BLK-S1-CONTRACT-01 | S1 | SAG-BE | alta | BLK-S1-ARCH-01 | 2026-06-26 | contratos de contexto |
| BLK-S1-DB-01 | S1 | SAG-DB | alta | BLK-S1-CONTRACT-01 | 2026-06-26 | mapa de schema 01-06 |
| BLK-S1-CI-01 | S1 | SAG-INT | media | BLK-S1-ARCH-01 | 2026-06-26 | pipeline inicial |
| BLK-S2-READ-01 | S2 | SAG-BE | alta | BLK-S1-CONTRACT-01 | 2026-06-26 | ids com fallback |
| BLK-S2-READ-02 | S2 | SAG-BE | alta | BLK-S2-READ-01 | 2026-06-26 | leitura ordenada |
| BLK-S2-READ-03 | S2 | SAG-BE | media | BLK-S2-READ-01 | 2026-06-26 | estatica com fallback |
| BLK-S2-OBS-01 | S2 | SAG-DB | alta | BLK-S1-DB-01 | 2026-06-26 | upsert transacional |
| BLK-S2-OBS-02 | S2 | SAG-BE | alta | BLK-S2-OBS-01 | 2026-06-26 | leitura/remocao |
| BLK-S2-TST-01 | S2 | SAG-QA | alta | BLK-S2-READ-02, BLK-S2-OBS-01 | 2026-06-26 | cenarios criticos |
| BLK-S3-UI-01 | S3 | SAG-FE | media | BLK-S2-READ-02 | 2026-06-26 | grafico multi-eixo |
| BLK-S3-UI-02 | S3 | SAG-FE | alta | BLK-S2-OBS-01, BLK-S2-OBS-02 | 2026-06-26 | editor observacao |
| BLK-S3-UI-03 | S3 | SAG-FE | media | BLK-S3-UI-01 | 2026-06-26 | identidade visual |
| BLK-S3-CSV-01 | S3 | SAG-BE | baixa | BLK-S2-READ-02 | 2026-06-26 | export csv |
| BLK-S3-PDF-01 | S3 | SAG-REPORT | alta | BLK-S2-READ-02 | 2026-06-26 | export pdf |
| BLK-S3-A11Y-01 | S3 | SAG-QA | media | BLK-S3-UI-03 | 2026-06-26 | acessibilidade |
| BLK-S4-PERF-01A | S4 | SAG-DB | media | BLK-S2-READ-02 | 2026-06-26 | baseline de tempos e IO |
| BLK-S4-PERF-01B | S4 | SAG-DB | alta | BLK-S4-PERF-01A | 2026-06-26 | indices compostos ID_Teste+LocalCol |
| BLK-S4-PERF-01C | S4 | SAG-DB | media | BLK-S4-PERF-01B | 2026-06-26 | revisar redundancia + sp_updatestats |
| BLK-S4-PERF-01D | S4 | SAG-BE | alta | BLK-S4-PERF-01C, BLK-S3-PDF-01 | 2026-06-26 | remover SELECT * estatico + benchmark |
| BLK-S4-REG-01 | S4 | SAG-QA | alta | BLK-S3-A11Y-01, BLK-S4-PERF-01D | 2026-06-26 | regressao |
| BLK-S4-DOC-01 | S4 | SAG-INT | baixa | BLK-S4-REG-01 | 2026-06-26 | documentacao final |
| BLK-S4-REL-01 | S4 | SAG-INT | alta | BLK-S4-REG-01, BLK-S4-DOC-01 | 2026-06-26 | release candidate |

### Doing

| backlog_id | sprint | owner_sag | started_at | updated_at | notes |
|---|---|---|---|---|---|
| - | - | - | - | 2026-06-26 | sem itens em andamento |

### Review

| backlog_id | sprint | owner_sag | updated_at | review_owner | notes |
|---|---|---|---|---|---|
| - | - | - | 2026-06-26 | - | sem itens em revisao |

### Done

| backlog_id | sprint | owner_sag | completed_at | evidence | notes |
|---|---|---|---|---|---|
| - | - | - | - | - | sem itens concluidos |

### Blocked

| backlog_id | sprint | owner_sag | blocked_reason | next_action | updated_at |
|---|---|---|---|---|---|
| - | - | - | - | - | 2026-06-26 |
