/*
Baseline de desempenho para recorte Cilindro_01..06.
Executar antes de aplicar indices compostos.
*/

SET NOCOUNT ON;
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

DECLARE @TestId NVARCHAR(255) = N'TESTE_2026_0001';

SELECT DISTINCT Cilindro_01_ID_Teste
FROM dbo.Cilindro_01
WHERE Cilindro_01_ID_Teste IS NOT NULL
ORDER BY Cilindro_01_ID_Teste;

SELECT LocalCol, Forca, Pressao_Compressor, Pressao_Reguladora, Temperatura_Ambiente
FROM dbo.Cilindro_01
WHERE Cilindro_01_ID_Teste = @TestId
ORDER BY LocalCol;

SELECT Cilindro_01_ID_Teste, Cilindro, Sensor_Cap, Tipo_Teste, Status_Ensaio,
       Setpoint, Duracao_Estimada, Temperatura_Inicial,
       Tempo_Inicial, Tempo_Final, Tempo_Decorrido_Total,
       Tempo_Decorrido_Parcial, Tempo_Decorrido_Ciclo, CreatedAt
FROM dbo.Cilindro_01_Estatico
WHERE Cilindro_01_ID_Teste = @TestId;

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
