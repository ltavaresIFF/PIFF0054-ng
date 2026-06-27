-- ============================================================
-- PROJETO_54_HP v2 - Schema de Alto Desempenho
-- ============================================================
-- Estratégia:
--   Leituras com CLUSTERED INDEX em (Cilindro_ID, Codigo_Teste, RowId)
--   → Consulta direta por cilindro + teste = clustered seek
--   → SEM JOIN, SEM key lookup, performance igual ao DB antigo
-- ============================================================

USE [master];
GO

IF DB_ID('Projeto_54_HP') IS NOT NULL
    DROP DATABASE [Projeto_54_HP];
GO

CREATE DATABASE [Projeto_54_HP];
GO

USE [Projeto_54_HP];
GO

-- ============================================================
-- 1. CILINDROS
-- ============================================================
CREATE TABLE dbo.Cilindros (
    Cilindro_ID   INT           NOT NULL IDENTITY(1,1),
    Nome_Cilindro VARCHAR(50)   NOT NULL,
    CreatedAt     DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Cilindros PRIMARY KEY CLUSTERED (Cilindro_ID)
);
GO

CREATE UNIQUE NONCLUSTERED INDEX IX_Cilindros_Nome 
    ON dbo.Cilindros(Nome_Cilindro);
GO

-- ============================================================
-- 2. ENSAIOS (metadados - tabela separada, sem impacto nas consultas)
-- ============================================================
CREATE TABLE dbo.Ensaios (
    Ensaio_ID              BIGINT        NOT NULL IDENTITY(1,1),
    Cilindro_ID            INT           NOT NULL,
    Codigo_Teste           VARCHAR(100)  NOT NULL,
    Sensor_Cap             VARCHAR(80)   NULL,
    Tipo_Teste             TINYINT       NULL,
    Status_Ensaio          VARCHAR(20)   NULL,
    Setpoint               NUMERIC(10,2) NULL,
    Duracao_Estimada_Horas NUMERIC(8,2)  NULL,
    Temperatura_Inicial    NUMERIC(5,2)  NULL,
    Tempo_Inicial          DATETIME2(0)  NULL,
    Tempo_Final            DATETIME2(0)  NULL,
    CreatedAt              DATETIME2(0)  NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Ensaios PRIMARY KEY CLUSTERED (Ensaio_ID),
    CONSTRAINT FK_Ensaios_Cilindros 
        FOREIGN KEY (Cilindro_ID) REFERENCES dbo.Cilindros(Cilindro_ID),
    CONSTRAINT UQ_Ensaios_Codigo_Teste UNIQUE (Codigo_Teste)
);
GO

CREATE NONCLUSTERED INDEX IX_Ensaios_Codigo_Teste
    ON dbo.Ensaios(Codigo_Teste)
    INCLUDE (Ensaio_ID, Cilindro_ID, Status_Ensaio, Setpoint, 
             Sensor_Cap, Tempo_Inicial, Tempo_Final);
GO

-- ============================================================
-- 3. LEITURAS (tabela principal de performance)
--    CLUSTERED INDEX: (Cilindro_ID, Codigo_Teste, RowId)
--    → Consulta SEM JOIN, busca direta!
-- ============================================================
CREATE TABLE dbo.Leituras (
    Cilindro_ID            INT            NOT NULL,
    Codigo_Teste           VARCHAR(100)   NOT NULL,
    RowId                  BIGINT         NOT NULL,
    TimeCol                DATETIME2(0)   NOT NULL,
    MSecCol                INT            NULL,
    LocalCol               INT            NOT NULL,
    UserCol                VARCHAR(80)    NULL,
    ReasonCol              VARCHAR(80)    NOT NULL DEFAULT '',
    Setpoint               NUMERIC(10,2)  NULL,
    Forca                  NUMERIC(10,2)  NULL,
    Pressao_Compressor     NUMERIC(10,2)  NULL,
    Pressao_Reguladora     NUMERIC(10,2)  NULL,
    Temperatura_Ambiente   NUMERIC(5,2)   NULL,
    Tipo_Teste             TINYINT        NULL,
    LeituraIndice          INT            NULL,
    Em_Alarme              BIT            NOT NULL DEFAULT 0,
    CreatedAt              DATETIME2(0)   NOT NULL DEFAULT GETDATE(),
    OBS                    VARCHAR(255)   NULL,
    val_obs                NUMERIC(10,2)  NULL,
    y_column_name          VARCHAR(255)   NULL,

    -- CLUSTERED: dados do mesmo cilindro+teste ficam contíguos no disco
    CONSTRAINT PK_Leituras PRIMARY KEY CLUSTERED (Cilindro_ID, Codigo_Teste, RowId)
);
GO

-- Índice para consultas por período (cross-cilindro)
CREATE NONCLUSTERED INDEX IX_Leituras_Periodo
    ON dbo.Leituras(TimeCol)
    INCLUDE (Cilindro_ID, Codigo_Teste, Forca, Temperatura_Ambiente, Em_Alarme)
    WITH (DATA_COMPRESSION = PAGE);
GO

-- Índice para consultas por tipo de teste + alarme
CREATE NONCLUSTERED INDEX IX_Leituras_TipoTeste
    ON dbo.Leituras(Tipo_Teste, Em_Alarme)
    INCLUDE (Cilindro_ID, Codigo_Teste, TimeCol, Forca, Temperatura_Ambiente)
    WITH (DATA_COMPRESSION = PAGE);
GO

-- Aplica compressão PAGE no clustered index principal
ALTER INDEX PK_Leituras ON dbo.Leituras 
    REBUILD WITH (DATA_COMPRESSION = PAGE);
GO

-- ============================================================
-- VIEW (apenas para conveniência, sem impacto em performance)
-- ============================================================
CREATE OR ALTER VIEW dbo.VW_LeiturasCompletas
AS
SELECT 
    l.*,
    c.Nome_Cilindro,
    e.Status_Ensaio,
    e.Sensor_Cap,
    e.Tipo_Teste AS Tipo_Teste_Ensaio,
    e.Duracao_Estimada_Horas,
    e.Temperatura_Inicial,
    e.Tempo_Inicial AS Ensaio_Tempo_Inicial,
    e.Tempo_Final AS Ensaio_Tempo_Final
FROM dbo.Leituras l
JOIN dbo.Cilindros c ON l.Cilindro_ID = c.Cilindro_ID
LEFT JOIN dbo.Ensaios e ON l.Codigo_Teste = e.Codigo_Teste;
GO

PRINT 'Projeto_54_HP v2 criado com sucesso!';
GO
