-- =====================================================
-- Criação do banco Projeto_54_ng e suas tabelas
-- =====================================================

-- Cria o banco de dados
IF DB_ID('Projeto_54_ng') IS NULL
BEGIN
    CREATE DATABASE [Projeto_54_ng];
END
GO

USE [Projeto_54_ng];
GO

-- 1. Cadastro de Cilindros
IF OBJECT_ID('dbo.Cilindros', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Cilindros (
        Cilindro_ID INT IDENTITY(1,1) CONSTRAINT PK_Cilindros PRIMARY KEY,
        Nome_Cilindro VARCHAR(50) NOT NULL,
        Capacidade_Sensor NUMERIC(10,2) NULL,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- 2. Ensaios Estáticos (Cabeçalho unificado)
IF OBJECT_ID('dbo.Ensaios_Estaticos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Ensaios_Estaticos (
        Ensaio_ID BIGINT IDENTITY(1,1) CONSTRAINT PK_Ensaios_Estaticos PRIMARY KEY,
        Cilindro_ID INT NOT NULL CONSTRAINT FK_EnsaiosEstaticos_Cilindros FOREIGN KEY REFERENCES dbo.Cilindros(Cilindro_ID),
        Codigo_Teste_Negocio VARCHAR(100) NOT NULL,
        Tipo_Teste VARCHAR(50) NULL,
        Status_Ensaio VARCHAR(20) NULL,
        Setpoint NUMERIC(10,2) NULL,
        Duracao_Estimada_Segundos INT NULL,
        Tempo_Inicial DATETIME NULL,
        Tempo_Final DATETIME NULL,
        CreatedAt DATETIME DEFAULT GETDATE(),
        CONSTRAINT UQ_Codigo_Teste UNIQUE (Codigo_Teste_Negocio)
    );
END
GO

-- 3. Ensaios Dados Dinâmicos (Série temporal unificada)
IF OBJECT_ID('dbo.Ensaios_Dados_Dinamicos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Ensaios_Dados_Dinamicos (
        RowId BIGINT IDENTITY(1,1) CONSTRAINT PK_Ensaios_Dados_Dinamicos PRIMARY KEY,
        Ensaio_ID BIGINT NOT NULL CONSTRAINT FK_DadosDinamicos_EnsaiosEstaticos FOREIGN KEY REFERENCES dbo.Ensaios_Estaticos(Ensaio_ID),
        TimeCol DATETIME NOT NULL,
        MSecCol INT NULL,
        LocalCol INT NOT NULL,
        Setpoint NUMERIC(10,2) NULL,
        Forca NUMERIC(10,2) NULL,
        Pressao_Compressor NUMERIC(10,2) NULL,
        Pressao_Reguladora NUMERIC(10,2) NULL,
        Temperatura_Ambiente NUMERIC(5,2) NULL,
        Em_Alarme BIT DEFAULT 0
    );
END
GO
