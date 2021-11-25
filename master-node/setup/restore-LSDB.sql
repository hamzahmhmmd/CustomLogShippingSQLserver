USE [master]

RESTORE DATABASE LSDB
FROM DISK = '/setup/LSDB.bak'
WITH
MOVE 'LSDB' TO '/var/opt/mssql/data/LSDB.MDF',
MOVE 'LSDB_LOG' TO '/var/opt/mssql/data/LSDB_Log.ldf', REPLACE    
GO

--USE [master]

--RESTORE DATABASE LSDB
--FROM DISK = '/setup/LSDB.bak'
--WITH MOVE 'LSDB' TO '/var/opt/mssql/data/LSDB.mdf',
--MOVE 'LSDB_Log' TO '/var/opt/mssql/data/LSDB_Log.ldf'
--GO