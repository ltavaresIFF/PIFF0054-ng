-- ============================================================
-- PROJETO_54_HP - Schema de Alto Desempenho
-- ============================================================
-- Estratégia de performance:
--   1. Cilindros (lookup, 13 linhas)
--   2. Ensaios (metadata, 300 linhas) com clustered PK + índices
--   3. Leituras (time-series, 30.000 linhas)
--      CLUSTERED INDEX em (Ensaio_ID, RowId)
--      → Todos os dados de um ensaio ficam contíguos no disco
--      → SELECT por Ensaio_ID = CLUSTERED SEEK (sem key lookup)
--   4. Dados dos cilindros 07-13 incluem colunas OBS opcionais
--      (schema unificado com todas as colunas)
-- ============================================================

IF DB_ID('Projeto_54_HP') IS NULL
    CREATE DATABASE [Projeto_54_HP];
GO

USE [Projeto_54_HP];
GO

-- ============================================================
-- 1. CILINDROS (lookup table)
-- ============================================================
IF OBJECT_ID('dbo.Cilindros', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Cilindros (
        Cilindro_ID   INT           NOT NULL IDENTITY(1,1),
        Nome_Cilindro VARCHAR(50)   NOT NULL,
        CreatedAt     DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
        
        CONSTRAINT PK_Cilindros PRIMARY KEY CLUSTERED (Cilindro_ID)
    );
END
GO

-- Índice para lookup por nome
CREATE UNIQUE NONCLUSTERED INDEX IX_Cilindros_Nome 
    ON dbo.Cilindros(Nome_Cilindro);
GO

-- ============================================================
-- 2. ENSAIOS (cabeçalho/meta dados - 1 por teste)
-- ============================================================
IF OBJECT_ID('dbo.Ensaios', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Ensaios (
        Ensaio_ID        BIGINT        NOT NULL IDENTITY(1,1),
        Cilindro_ID      INT           NOT NULL,
        Codigo_Teste     VARCHAR(100)  NOT NULL,
        Sensor_Cap       VARCHAR(80)   NULL,
        Tipo_Teste       TINYINT       NULL,
        Status_Ensaio    VARCHAR(20)   NULL,
        Setpoint         NUMERIC(10,2) NULL,
        Duracao_Estimada_Horas NUMERIC(8,2) NULL,
        Temperatura_Inicial NUMERIC(5,2) NULL,
        Tempo_Inicial    DATETIME2(0)  NULL,
        Tempo_Final      DATETIME2(0)  NULL,
        CreatedAt        DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
        
        CONSTRAINT PK_Ensaios PRIMARY KEY CLUSTERED (Ensaio_ID),
        CONSTRAINT FK_Ensaios_Cilindros 
            FOREIGN KEY (Cilindro_ID) REFERENCES dbo.Cilindros(Cilindro_ID),
        CONSTRAINT UQ_Ensaios_Codigo_Teste UNIQUE (Codigo_Teste)
    );
END
GO

-- Índice covering para JOIN + WHERE frequentes
CREATE NONCLUSTERED INDEX IX_Ensaios_Busca
    ON dbo.Ensaios(Cilindro_ID, Codigo_Teste)
    INCLUDE (Ensaio_ID, Status_Ensaio, Setpoint, Tempo_Inicial, Tempo_Final);
GO

-- ============================================================
-- 3. LEITURAS (time-series - tabela principal de performance)
-- ============================================================
-- CLUSTERED INDEX em (Ensaio_ID, RowId) → armazenamento contíguo
-- por ensaio → clustered seek direto sem key lookup
-- ============================================================
IF OBJECT_ID('dbo.Leituras', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Leituras (
        Ensaio_ID            BIGINT        NOT NULL,
        RowId                BIGINT        NOT NULL,
        TimeCol              DATETIME2(0)  NOT NULL,
        MSecCol              INT           NULL,
        LocalCol             INT           NOT NULL,
        UserCol              VARCHAR(80)   NULL,
        ReasonCol            VARCHAR(80)   NOT NULL DEFAULT '',
        Setpoint             NUMERIC(10,2) NULL,
        Forca                NUMERIC(10,2) NULL,
        Pressao_Compressor   NUMERIC(10,2) NULL,
        Pressao_Reguladora   NUMERIC(10,2) NULL,
        Temperatura_Ambiente NUMERIC(5,2)  NULL,
        Tipo_Teste           TINYINT       NULL,
        LeituraIndice        INT           NULL,
        Em_Alarme            BIT           NOT NULL DEFAULT 0,
        CreatedAt            DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
        OBS                  VARCHAR(255)  NULL,
        val_obs              NUMERIC(10,2) NULL,
        y_column_name        VARCHAR(255)  NULL,
        
        -- Clusterizado por Ensaio_ID → dados contíguos no disco
        CONSTRAINT PK_Leituras PRIMARY KEY CLUSTERED (Ensaio_ID, RowId),
        CONSTRAINT FK_Leituras_Ensaios 
            FOREIGN KEY (Ensaio_ID) REFERENCES dbo.Ensaios(Ensaio_ID)
    );
END
GO

-- Índice para consultas por período (cross-ensaio)
CREATE NONCLUSTERED INDEX IX_Leituras_Periodo
    ON dbo.Leituras(TimeCol)
    INCLUDE (Ensaio_ID, Forca, Pressao_Compressor, Temperatura_Ambiente, Em_Alarme);
GO

-- Índice para consultas por tipo de teste + alarme
CREATE NONCLUSTERED INDEX IX_Leituras_TipoTeste
    ON dbo.Leituras(Tipo_Teste, Em_Alarme)
    INCLUDE (Ensaio_ID, TimeCol, Forca, Temperatura_Ambiente);
GO

-- ============================================================
-- VIEWS DE CONVENIÊNCIA
-- ============================================================

-- View que junta tudo (para queries ad-hoc)
GO
CREATE OR ALTER VIEW dbo.VW_LeiturasCompletas
AS
SELECT 
    l.*,
    e.Codigo_Teste,
    e.Sensor_Cap,
    e.Status_Ensaio,
    e.Tempo_Inicial AS Ensaio_Tempo_Inicial,
    e.Tempo_Final AS Ensaio_Tempo_Final,
    e.Duracao_Estimada_Horas,
    e.Temperatura_Inicial,
    c.Nome_Cilindro
FROM dbo.Leituras l
JOIN dbo.Ensaios e ON l.Ensaio_ID = e.Ensaio_ID
JOIN dbo.Cilindros c ON e.Cilindro_ID = c.Cilindro_ID;
GO

PRINT 'Banco Projeto_54_HP criado com sucesso!';
GO
