-- ============================================================
-- PROJETO_54_HP v3 - Schema Final Otimizado
-- ============================================================
-- Estratégia:
--   Leituras: só colunas dinâmicas (mesma largura da tabela original)
--   Ensaios: metadados separados (300 linhas, tabela pequena)
--   Clustered index em (Ensaio_ID, RowId) → dados contíguos
--   Consulta em 2 passos: lookup Ensaio_ID → clustered seek Leituras
-- ============================================================

USE [master];
GO

IF DB_ID('Projeto_54_HP') IS NOT NULL
BEGIN
    ALTER DATABASE [Projeto_54_HP] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [Projeto_54_HP];
END
GO

CREATE DATABASE [Projeto_54_HP];
GO

USE [Projeto_54_HP];
GO

-- ============================================================
-- 1. CILINDROS (lookup)
-- ============================================================
CREATE TABLE dbo.Cilindros (
    Cilindro_ID   INT          NOT NULL IDENTITY(1,1),
    Nome_Cilindro VARCHAR(50)  NOT NULL,
    CreatedAt     DATETIME2(0) NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Cilindros PRIMARY KEY CLUSTERED (Cilindro_ID)
);
GO
CREATE UNIQUE NONCLUSTERED INDEX IX_Cilindros_Nome ON dbo.Cilindros(Nome_Cilindro);
GO

-- ============================================================
-- 2. ENSAIOS (metadados - 300 linhas)
-- ============================================================
CREATE TABLE dbo.Ensaios (
    Ensaio_ID             BIGINT        NOT NULL IDENTITY(1,1),
    Cilindro_ID           INT           NOT NULL,
    Codigo_Teste          VARCHAR(100)  NOT NULL,
    Sensor_Cap            VARCHAR(80)   NULL,
    Tipo_Teste            TINYINT       NULL,
    Status_Ensaio         VARCHAR(20)   NULL,
    Setpoint              NUMERIC(10,2) NULL,
    Duracao_Estimada_Horas NUMERIC(8,2) NULL,
    Temperatura_Inicial   NUMERIC(5,2)  NULL,
    Tempo_Inicial         DATETIME2(0)  NULL,
    Tempo_Final           DATETIME2(0)  NULL,
    CreatedAt             DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
    
    CONSTRAINT PK_Ensaios PRIMARY KEY CLUSTERED (Ensaio_ID),
    CONSTRAINT FK_Ensaios_Cilindros FOREIGN KEY (Cilindro_ID) REFERENCES dbo.Cilindros(Cilindro_ID),
    CONSTRAINT UQ_Ensaios_Codigo_Teste UNIQUE (Codigo_Teste)
);
GO

-- Índice covering para lookup rápido por (Cilindro_ID, Codigo_Teste)
CREATE NONCLUSTERED INDEX IX_Ensaios_Busca
    ON dbo.Ensaios(Cilindro_ID, Codigo_Teste)
    INCLUDE (Ensaio_ID, Status_Ensaio, Setpoint, Sensor_Cap, Tempo_Inicial, Tempo_Final);
GO

-- ============================================================
-- 3. LEITURAS (time-series - colunas DINÂMICAS apenas)
--    MESMA LARGURA das tabelas Cilindro_XX originais
--    CLUSTERED INDEX em (Ensaio_ID, RowId) → dados contíguos
-- ============================================================
CREATE TABLE dbo.Leituras (
    Ensaio_ID            BIGINT         NOT NULL,
    RowId                BIGINT         NOT NULL,
    TimeCol              DATETIME2(0)   NOT NULL,
    MSecCol              INT            NULL,
    LocalCol             INT            NOT NULL,
    UserCol              VARCHAR(80)    NULL,
    ReasonCol            VARCHAR(80)    NOT NULL DEFAULT '',
    Setpoint             NUMERIC(10,2)  NULL,
    Forca                NUMERIC(10,2)  NULL,
    Pressao_Compressor   NUMERIC(10,2)  NULL,
    Pressao_Reguladora   NUMERIC(10,2)  NULL,
    Temperatura_Ambiente NUMERIC(5,2)   NULL,
    Tipo_Teste           TINYINT        NULL,
    LeituraIndice        INT            NULL,
    Em_Alarme            BIT            NOT NULL DEFAULT 0,
    CreatedAt            DATETIME2(0)   NOT NULL DEFAULT GETDATE(),
    OBS                  VARCHAR(255)   NULL,
    val_obs              NUMERIC(10,2)  NULL,
    y_column_name        VARCHAR(255)   NULL,

    -- CLUSTERED: (Ensaio_ID, RowId) → dados contíguos por ensaio
    CONSTRAINT PK_Leituras PRIMARY KEY CLUSTERED (Ensaio_ID, RowId),
    CONSTRAINT FK_Leituras_Ensaios FOREIGN KEY (Ensaio_ID) REFERENCES dbo.Ensaios(Ensaio_ID)
);
GO

-- Índices auxiliares
CREATE NONCLUSTERED INDEX IX_Leituras_Periodo
    ON dbo.Leituras(TimeCol)
    INCLUDE (Ensaio_ID, Forca, Temperatura_Ambiente, Em_Alarme);
GO

CREATE NONCLUSTERED INDEX IX_Leituras_TipoTeste
    ON dbo.Leituras(Tipo_Teste, Em_Alarme)
    INCLUDE (Ensaio_ID, TimeCol, Forca);
GO

-- Compressão PAGE
ALTER INDEX PK_Leituras ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
ALTER INDEX IX_Leituras_Periodo ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
ALTER INDEX IX_Leituras_TipoTeste ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
GO

-- ============================================================
-- VIEW CONSOLIDADA (para consultas ad-hoc)
-- ============================================================
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

PRINT 'Projeto_54_HP v3 criado com sucesso!';
GO
