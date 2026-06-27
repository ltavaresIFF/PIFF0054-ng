/*
Passo posterior ao create index: revisar potenciais redundancias e atualizar estatisticas.
*/

SET NOCOUNT ON;

SELECT
    t.name AS table_name,
    i.name AS index_name,
    i.type_desc,
    i.is_unique,
    i.has_filter,
    i.filter_definition
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
WHERE t.name IN (
    'Cilindro_01','Cilindro_02','Cilindro_03','Cilindro_04','Cilindro_05','Cilindro_06'
)
  AND i.index_id > 0
ORDER BY t.name, i.name;

EXEC sp_updatestats;
