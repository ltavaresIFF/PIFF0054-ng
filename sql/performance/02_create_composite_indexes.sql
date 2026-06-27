/*
Pacote minimo NFR-008: indices compostos por (ID_Teste, LocalCol) no recorte 01-06.
Script idempotente.
*/

SET NOCOUNT ON;

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_01_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_01')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_01_ID_Teste_LocalCol
ON dbo.Cilindro_01 (Cilindro_01_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_02_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_02')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_02_ID_Teste_LocalCol
ON dbo.Cilindro_02 (Cilindro_02_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_03_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_03')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_03_ID_Teste_LocalCol
ON dbo.Cilindro_03 (Cilindro_03_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_04_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_04')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_04_ID_Teste_LocalCol
ON dbo.Cilindro_04 (Cilindro_04_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_05_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_05')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_05_ID_Teste_LocalCol
ON dbo.Cilindro_05 (Cilindro_05_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_Cilindro_06_ID_Teste_LocalCol'
      AND object_id = OBJECT_ID('dbo.Cilindro_06')
)
CREATE NONCLUSTERED INDEX IX_Cilindro_06_ID_Teste_LocalCol
ON dbo.Cilindro_06 (Cilindro_06_ID_Teste, LocalCol)
INCLUDE (Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente, Tipo_Teste, LeituraIndice, Em_Alarme);
