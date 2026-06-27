-- ============================================================
-- PROJETO_54_HP v2 - Schema de Máximo Desempenho
-- ============================================================
-- Estratégia:
--   Clustered Index em (Cilindro_ID, Codigo_Teste, RowId)
--   → Dados de um cilindro + teste ficam CONTÍGUOS no disco
--   → SELECT sem JOIN: busca direta por Cilindro_ID + Codigo_Teste
--   → Performance igual ao banco antigo, schema unificado
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
-- 2. LEITURAS (tabela única - sem JOIN para consulta direta)
-- ============================================================
-- CLUSTERED INDEX em (Cilindro_ID, Codigo_Teste, RowId)
--   → Dados contíguos por (cilindro, teste)
--   → SELECT * WHERE Cilindro_ID=X AND Codigo_Teste='Y' = CLUSTERED SEEK
--   → SEM JOIN com Ensaios ou Cilindros para consultas de leitura!
-- ============================================================
CREATE TABLE dbo.Leituras (
    Cilindro_ID          INT            NOT NULL,
    Codigo_Teste         VARCHAR(100)   NOT NULL,
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
    Sensor_Cap           VARCHAR(80)    NULL,
    Status_Ensaio        VARCHAR(20)    NULL,
    Duracao_Estimada_Horas NUMERIC(8,2) NULL,
    Temperatura_Inicial  NUMERIC(5,2)   NULL,
    Tempo_Inicial        DATETIME2(0)   NULL,
    Tempo_Final          DATETIME2(0)   NULL,

    -- CLUSTERED: (Cilindro_ID, Codigo_Teste, RowId)
    -- → Todos os dados de um cilindro+teste contíguos no disco
    CONSTRAINT PK_Leituras PRIMARY KEY CLUSTERED (Cilindro_ID, Codigo_Teste, RowId)
);
GO

-- Índices auxiliares (para consultas analíticas)
CREATE NONCLUSTERED INDEX IX_Leituras_Periodo
    ON dbo.Leituras(TimeCol)
    INCLUDE (Cilindro_ID, Codigo_Teste, Forca, Pressao_Compressor, Temperatura_Ambiente, Em_Alarme);
GO

CREATE NONCLUSTERED INDEX IX_Leituras_TipoTeste
    ON dbo.Leituras(Tipo_Teste, Em_Alarme)
    INCLUDE (Cilindro_ID, Codigo_Teste, TimeCol, Forca, Temperatura_Ambiente);
GO

-- Índice para lookup de ensaio por RowId original
CREATE UNIQUE NONCLUSTERED INDEX IX_Leituras_RowId
    ON dbo.Leituras(RowId);
GO

-- ============================================================
-- Compressão PAGE
-- ============================================================
ALTER INDEX PK_Leituras ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
ALTER INDEX IX_Leituras_Periodo ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
ALTER INDEX IX_Leituras_TipoTeste ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
ALTER INDEX IX_Leituras_RowId ON dbo.Leituras REBUILD WITH (DATA_COMPRESSION = PAGE);
GO

PRINT 'Projeto_54_HP v2 criado com sucesso!';
GO
