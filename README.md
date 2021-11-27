# Custom Log Shipping SQL Server

![alt text](https://raw.githubusercontent.com/hamzahmhmmd/CustomLogShippingSQLserver/master/images/Custom%20log%20shipping%20architecture.jpg?token=ALAAYUEEDQMBBOYWPBXLGDLBUXIGC "Custom Log Shipping Architecture")

> semua code yang ada pada repo ini adalah query SQL, kecuali yang dimulai dengan `->` yaitu shell command pada windows (dapat dijalankan pada linux dengan penyesuaian), `$` yaitu linux shell command, dan `>` yaitu script mongodb

## Reproduksi berbasis Docker
Solusi berbasis docker ini berisi **master instance**: `SQLMASTERc` (custom mssql image), **backup instance**: `SQLLS1c` dan `SQLLS2c` (official mssql image), **mongo db server**: `MONGOc` (official mongo image), **Web App server**: `WEBAPP` (custom python image), terhubung dalam satu subnet `10.10.0.0/16` dan dua buah dockeer volume untuk masing-masing backup instance yang diinstall dengan docker-compose. 

### Alat dan bahan
- Docker desktop (di test pada windows 11 dengan WSL2 backedend, namun seharusnya tidak masalah apapun host OS nya)
- SSMS (recommended, karena dapat mengobservasi linked server) atau sejenisnya
- Jaringan internet, karena harus mendownload docker image yang besar

### Cara Pembuatan
1. Clone repo ini dan masuk kedalam foldernya.

#### Pembuatan docker image
2. Pembuatan docker image untuk SQLMASTER dan web app. Pertama tama masuk ke dalam folder `master-node/` dan jalankan perintah
```
-> docker build -t mssql2019-lsdb-linked:2 .
```
3. selanjutnya masuk ke folder `web-app/` dan jalankan perintah
```
-> docker build -t log-shipping-web-app:4 .
```
4. check docker image anda, pastikan bertambah 2 item yaitu `mssql2019-lsdb-linked` dan `log-shipping-web-app` 

#### Pebuatan container
5. keluar dari folder `web-app/` dan jalankan perintah
```
-> docker-compose up -d
```
6. pastikan terdapat container group baru seperti gambar dibawah.

![alt text](https://raw.githubusercontent.com/hamzahmhmmd/CustomLogShippingSQLserver/docker-solution/images/Custom%20log%20shipping%20webapp%20docker.png?token=ALAAYUCX3TUBSZNSJLPN4V3BVBTUK "Custom Log Shipping Docker")

#### Pembuatan linked server
7. masuk ke instance `SQLMASTERc` melalui ssms dengan server `localhost,1336` dan user `SA` dan password `Root05211840000048`
8. tambahkan backup instance `SQLLS1c` dan `SQLLS2c` sebagai linked server dengan perintah
```
DECLARE @s NVARCHAR(128) = N'.\SQLLS1',
        @t NVARCHAR(128) = N'true',
        @p NVARCHAR(128) = N'MSOLEDBSQL',
        @i NVARCHAR(128) = N'10.10.10.12,1433';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'', @provider = @p,  @datasrc  = @i;
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
GO

DECLARE @s NVARCHAR(128) = N'.\SQLLS2',
        @t NVARCHAR(128) = N'true',
        @p NVARCHAR(128) = N'MSOLEDBSQL',
        @i NVARCHAR(128) = N'10.10.10.12,1433';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'', @provider = @p,  @datasrc  = @i;
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
```

#### Pembuatan initial backup
9. selanjutnya memberikan permision user `mssql` pada master instance untuk menulis di volume `ls-transport` yang menempel pada `/tmp` masing-masing instance
```
-> sudo docker exec -u 0 SQLMASTERc bash -c "chown mssql /tmp"
```
10. lakukan insiasi backup pertama kali dengan query berikut pada ssms
```
EXEC dbo.PMAG_Backup @dbname = N'LSDB', @type = 'bak', @init = 1;
```
11. jika berhasil, dapat dicoba untuk melakukan log backup dengan SP yang sama namun dengan parameter  `type = trn` 
```
EXEC dbo.PMAG_Backup @dbname = N'LSDB', @type = 'trn';
```

#### Penggunaan Web App
12. setelah semua berhasil silahkan buka webapp pada browser dengan alamat `localhost:8503` dan cara penggunaannya dapat dilihat di [sini](https://github.com/hamzahmhmmd/CustomLogShippingSQLserver/tree/docker-solution#cara-penggunaan-web-app) 

![alt text](https://raw.githubusercontent.com/hamzahmhmmd/CustomLogShippingSQLserver/master/images/Custom%20log%20shipping%20webapp.png?token=ALAAYUHLDKCCDU7Z6Y5EMP3BUXIMW "Custom Log Shipping Web App")

#### Pembuatan cron jobs
13. terakhir adalah membuat cron jobs untuk log backup tiap 15 menit dan menghapus file backup setiap 7 hari. pertama-tama kita harus masuk ke dalam container `SQLMASTERc` dengan perintah
```
-> 
```
dan di dalam container tersebut jalankan perintah
```
$ 
```

## Reproduksi non-Docker
Solusi non-docker ini tidak hanya dapat dilakukan tanpa docker, tetap dapat menggunakan docker container namun dengan penyesuaian. Solusi ini memiliki kelebihan karena sistem oprasi windows dapat digunakan sebagai metode autentikasi setiap instance mssql sehingga lebih mudah dibanding docker yang berbasis linux.

### Alat dan Bahan
- Windows (ditest pada Windows 11 Home edition)
- SQL server 2019 Express Edition, pada project ini menggunakan windows user authentication
- SSMS (recommended, karena dapat mengobservasi linked server) atau sejenisnya
- SQLCMD, cek `SQLCMD -?`, jika error install dari https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility
- FORFILES, cek `FORFILES -?`
- VENV Python 3.8, cek `python --version`
- Mongodb v5.0.4, cek `mongo`

### Cara pembuatan
1. git clone repo ini `git clone https://github.com/hamzahmhmmd/CustomLogShippingSQLserver.git`
2. install semua alat dan bahan, minimal 3 SQLserver, pada hal ini 
      - **master instance** : `localhost\SQLDEV`,
      - **backup instance** : `localhost\SQLLS1`, dan 
      - **backup instance** : `localhost\SQLLS2`
3. install `requirements.txt`
4. setelah itu membuat link dari **master** ke semua **backup** instance, pada hal ini `localhost\SQLLS1`
```
USE [master];
GO
DECLARE @s NVARCHAR(128) = N'.\SQLLS1',
        @t NVARCHAR(128) = N'true';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'SQL Server';
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
```
dan untuk `localhost\SQLLS2`
```
USE [master];
GO
DECLARE @s NVARCHAR(128) = N'.\SQLLS2',
        @t NVARCHAR(128) = N'true';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'SQL Server';
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
```
5. lalu pada instance **master** buat database `LSDB`. Database ini akan berisi beberapa tabel seperti gambar dibawah dan membuat mode recovery FULL dengan 
```
USE [master];
CREATE DATABASE LSDB;
ALTER DATABASE LSDB SET RECOVERY FULL;
```
![alt text](https://raw.githubusercontent.com/hamzahmhmmd/CustomLogShippingSQLserver/master/images/Custom%20log%20shipping%20ERD.png?token=ALAAYUBGANWVXGXON4KECKTBUXIYS "Custom Log Shipping ERD")
6. selanjutnya membuat tabel-table diatas, pertamatama tabel `PMAG_Databases` dimana menampung informasi nama database apa yang akan dibackup. Selanjutnya  table `PMAG_Secondaries` yang akan berisi informasi mengenai backup instance. Table berikutnya adalah table `PMAG_LogBackupHistory` yang menampung informasi log backup yang berhasil dilakukan. Table terakhir `PMAG_LogRestoreHistory` adalah tabel yang menampung informasi file log apa yang berhasil ter-restore
```
USE [LSDB];
GO
CREATE TABLE dbo.PMAG_Databases
(
  DatabaseName               SYSNAME,
  LogBackupFrequency_Minutes SMALLINT NOT NULL DEFAULT (15),
  CONSTRAINT PK_DBS PRIMARY KEY(DatabaseName)
);
GO

CREATE TABLE dbo.PMAG_Secondaries
(
  DatabaseName     SYSNAME,
  ServerInstance   SYSNAME,
  CommonFolder     VARCHAR(512) NOT NULL,
  DataFolder       VARCHAR(512) NOT NULL,
  LogFolder        VARCHAR(512) NOT NULL,
  StandByLocation  VARCHAR(512) NOT NULL,
  IsCurrentStandby BIT NOT NULL DEFAULT 0,
  CONSTRAINT PK_Sec PRIMARY KEY(DatabaseName, ServerInstance),
  CONSTRAINT FK_Sec_DBs FOREIGN KEY(DatabaseName)
    REFERENCES dbo.PMAG_Databases(DatabaseName)
);
GO

CREATE TABLE dbo.PMAG_LogBackupHistory
(
  DatabaseName   SYSNAME,
  ServerInstance SYSNAME,
  BackupSetID    INT NOT NULL,
  Location       VARCHAR(2000) NOT NULL,
  BackupTime     DATETIME NOT NULL DEFAULT SYSDATETIME(),
  CONSTRAINT PK_LBH PRIMARY KEY(DatabaseName, ServerInstance, BackupSetID),
  CONSTRAINT FK_LBH_DBs FOREIGN KEY(DatabaseName)
    REFERENCES dbo.PMAG_Databases(DatabaseName),
  CONSTRAINT FK_LBH_Sec FOREIGN KEY(DatabaseName, ServerInstance)
    REFERENCES dbo.PMAG_Secondaries(DatabaseName, ServerInstance)
);
GO

CREATE TABLE dbo.PMAG_LogRestoreHistory
(
  DatabaseName   SYSNAME,
  ServerInstance SYSNAME,
  BackupSetID    INT,
  RestoreTime    DATETIME,
  CONSTRAINT PK_LRH PRIMARY KEY(DatabaseName, ServerInstance, BackupSetID),
  CONSTRAINT FK_LRH_DBs FOREIGN KEY(DatabaseName)
    REFERENCES dbo.PMAG_Databases(DatabaseName),
  CONSTRAINT FK_LRH_Sec FOREIGN KEY(DatabaseName, ServerInstance)
    REFERENCES dbo.PMAG_Secondaries(DatabaseName, ServerInstance)
);
GO
```
10. selanjutnya membuat **store procedure** untuk menangani proses backup pada database `LSDB`
```
CREATE OR ALTER PROCEDURE [dbo].[PMAG_Backup]
  @dbname SYSNAME,
  @type   CHAR(3) = 'bak', -- or 'trn'
  @init   BIT     = 0 -- only used with 'bak'
AS
BEGIN
  SET NOCOUNT ON;
 
  -- generate a filename pattern
  DECLARE @now DATETIME = SYSDATETIME();
  DECLARE @fn NVARCHAR(256) = @dbname + N'_' + CONVERT(CHAR(8), @now, 112) 
    + RIGHT(REPLICATE('0',6) + CONVERT(VARCHAR(32), DATEDIFF(SECOND, 
      CONVERT(DATE, @now), @now)), 6) + N'.' + @type;
 
  -- generate a backup command with MIRROR TO for each distinct CommonFolder
  DECLARE @sql NVARCHAR(MAX) = N'BACKUP' 
    + CASE @type WHEN 'bak' THEN N' DATABASE ' ELSE N' LOG ' END
    + QUOTENAME(@dbname) + ' 
    ' + STUFF(
        (SELECT DISTINCT CHAR(13) + CHAR(10) + N' MIRROR TO DISK = ''' 
           + s.CommonFolder + @fn + ''''
         FROM dbo.PMAG_Secondaries AS s 
         WHERE s.DatabaseName = @dbname 
         FOR XML PATH(''), TYPE).value(N'.[1]',N'nvarchar(max)'),1,9,N'') + N' 
        WITH NAME = N''' + @dbname + CASE @type 
        WHEN 'bak' THEN N'_PMAGFull' ELSE N'_PMAGLog' END 
        + ''', INIT, FORMAT' + CASE WHEN LEFT(CONVERT(NVARCHAR(128), 
        SERVERPROPERTY(N'Edition')), 3) IN (N'Dev', N'Ent')
        THEN N', COMPRESSION;' ELSE N';' END;
 
  EXEC [master].sys.sp_executesql @sql;
 
  IF @type = 'bak' AND @init = 1  -- initialize log shipping
  BEGIN
    EXEC dbo.PMAG_InitializeSecondaries @dbname = @dbname, @fn = @fn;
  END
 
  IF @type = 'trn'
  BEGIN
    -- record the fact that we backed up a log
    INSERT dbo.PMAG_LogBackupHistory
    (
      DatabaseName, 
      ServerInstance, 
      BackupSetID, 
      Location
    )
    SELECT 
      DatabaseName = @dbname, 
      ServerInstance = s.ServerInstance, 
      BackupSetID = MAX(b.backup_set_id), 
      Location = s.CommonFolder + @fn
    FROM msdb.dbo.backupset AS b
    CROSS JOIN dbo.PMAG_Secondaries AS s
    WHERE b.name = @dbname + N'_PMAGLog'
      AND s.DatabaseName = @dbname
    GROUP BY s.ServerInstance, s.CommonFolder + @fn;
 
    -- once we've backed up logs, 
    -- restore them on the next secondary
    EXEC dbo.PMAG_RestoreLogs @dbname = @dbname;
  END
END
```
11. Selanjutnya membuat SP `PMAG_InitializeSecondaries` yang digunakan untuk FULL backup sebagai inisiasi awal log shipping
```
CREATE OR ALTER PROCEDURE dbo.PMAG_InitializeSecondaries
  @dbname SYSNAME,
  @fn     VARCHAR(512)
AS
BEGIN
  SET NOCOUNT ON;
 
  -- clear out existing history/settings (since this may be a re-init)
  DELETE dbo.PMAG_LogBackupHistory  WHERE DatabaseName = @dbname;
  DELETE dbo.PMAG_LogRestoreHistory WHERE DatabaseName = @dbname;
  UPDATE dbo.PMAG_Secondaries SET IsCurrentStandby = 0
    WHERE DatabaseName = @dbname;
 
  DECLARE @sql   NVARCHAR(MAX) = N'',
          @files NVARCHAR(MAX) = N'';
 
  -- need to know the logical file names - may be more than two
  SET @sql = N'SELECT @files = (SELECT N'', MOVE N'''''' + name 
    + '''''' TO N''''$'' + CASE [type] WHEN 0 THEN N''df''
      WHEN 1 THEN N''lf'' END + ''$''''''
    FROM ' + QUOTENAME(@dbname) + '.sys.database_files
    WHERE [type] IN (0,1)
    FOR XML PATH, TYPE).value(N''.[1]'',N''nvarchar(max)'');';
 
  EXEC master.sys.sp_executesql @sql,
    N'@files NVARCHAR(MAX) OUTPUT', 
    @files = @files OUTPUT;
 
  SET @sql = N'';
 
  -- restore - need physical paths of data/log files for WITH MOVE
  -- this can fail, obviously, if those path+names already exist for another db
  SELECT @sql += N'EXEC ' + QUOTENAME(ServerInstance) 
    + N'.master.sys.sp_executesql N''RESTORE DATABASE ' + QUOTENAME(@dbname) 
    + N' FROM DISK = N''''' + CommonFolder + @fn + N'''''' + N' WITH REPLACE, 
      NORECOVERY' + REPLACE(REPLACE(REPLACE(@files, N'$df$', DataFolder 
    + @dbname + N'.mdf'), N'$lf$', LogFolder + @dbname + N'.ldf'), N'''', N'''''') 
    + N';'';' + CHAR(13) + CHAR(10)
  FROM dbo.PMAG_Secondaries
  WHERE DatabaseName = @dbname;
 
  EXEC [master].sys.sp_executesql @sql;
 
  -- backup a log for this database
  EXEC dbo.PMAG_Backup @dbname = @dbname, @type = 'trn';
 
  -- restore logs
  EXEC dbo.PMAG_RestoreLogs @dbname = @dbname, @PrepareAll = 1;
END
```
12. selanjutnya adalah pembuata SP `PMAG_RestoreLogs` yang digunakan untu proses restore setiap backup
```
CREATE OR ALTER PROCEDURE dbo.PMAG_RestoreLogs
  @dbname     SYSNAME,
  @PrepareAll BIT = 0
AS
BEGIN
  SET NOCOUNT ON;
 
  DECLARE @StandbyInstance SYSNAME,
          @CurrentInstance SYSNAME,
          @BackupSetID     INT, 
          @Location        VARCHAR(512),
          @StandByLocation VARCHAR(512),
          @sql             NVARCHAR(MAX),
          @rn              INT,
          @NumOfNode       INT;
 
  -- if number of backup node is 1 than use that only one node as @StandbyInstance else, get next standby node
  SELECT @NumOfNode = COUNT(DatabaseName) from dbo.PMAG_Secondaries WHERE DatabaseName = @dbname
  
  IF @NumOfNode = 1
    SELECT @StandbyInstance = MIN(ServerInstance)
    FROM dbo.PMAG_Secondaries
    WHERE DatabaseName = @dbname
    
  ELSE
    SELECT @StandbyInstance = MIN(ServerInstance)
      FROM dbo.PMAG_Secondaries
      WHERE IsCurrentStandby = 0
        AND ServerInstance > (SELECT ServerInstance
      FROM dbo.PMAG_Secondaries
      WHERE IsCurrentStandBy = 1 AND DatabaseName = @dbname);
 
    IF @StandbyInstance IS NULL -- either it was last or a re-init
    BEGIN
      SELECT @StandbyInstance = MIN(ServerInstance)
        FROM dbo.PMAG_Secondaries;
    END
 
  -- get that instance up and into STANDBY
  -- for each log in logbackuphistory not in logrestorehistory:
  -- restore, and insert it into logrestorehistory
  -- mark the last one as STANDBY
  -- if @prepareAll is true, mark all others as NORECOVERY
  -- in this case there should be only one, but just in case
 
  DECLARE c CURSOR LOCAL FAST_FORWARD FOR 
    SELECT bh.BackupSetID, s.ServerInstance, bh.Location, s.StandbyLocation,
      rn = ROW_NUMBER() OVER (PARTITION BY s.ServerInstance ORDER BY bh.BackupSetID DESC)
    FROM dbo.PMAG_LogBackupHistory AS bh
    INNER JOIN dbo.PMAG_Secondaries AS s
    ON bh.DatabaseName = s.DatabaseName
    AND bh.ServerInstance = s.ServerInstance
    WHERE s.DatabaseName = @dbname
    AND s.ServerInstance = CASE @PrepareAll 
	WHEN 1 THEN s.ServerInstance ELSE @StandbyInstance END
    AND NOT EXISTS
    (
      SELECT 1 FROM dbo.PMAG_LogRestoreHistory AS rh
        WHERE DatabaseName = @dbname
        AND ServerInstance = s.ServerInstance
        AND BackupSetID = bh.BackupSetID
    )
    ORDER BY CASE s.ServerInstance 
      WHEN @StandbyInstance THEN 1 ELSE 2 END, bh.BackupSetID;
 
  OPEN c;
 
  FETCH c INTO @BackupSetID, @CurrentInstance, @Location, @StandbyLocation, @rn;
 
  WHILE @@FETCH_STATUS != -1
  BEGIN
    -- kick users out - set to single_user then back to multi
    SET @sql = N'EXEC ' + QUOTENAME(@CurrentInstance) + N'.[master].sys.sp_executesql '
    + 'N''IF EXISTS (SELECT 1 FROM sys.databases WHERE name = N''''' 
	+ @dbname + ''''' AND [user_access] = 0 AND [STATE] = 0)
	  BEGIN
	    ALTER DATABASE ' + QUOTENAME(@dbname) + N' SET SINGLE_USER '
      +   N'WITH ROLLBACK IMMEDIATE;
	    ALTER DATABASE ' + QUOTENAME(@dbname) + N' SET MULTI_USER;
	  END;'';';
 
    EXEC [master].sys.sp_executesql @sql;
 
    -- restore the log (in STANDBY if it's the last one):
    SET @sql = N'EXEC ' + QUOTENAME(@CurrentInstance) 
      + N'.[master].sys.sp_executesql ' + N'N''RESTORE LOG ' + QUOTENAME(@dbname) 
      + N' FROM DISK = N''''' + @Location + N''''' WITH ' + CASE WHEN @rn = 1 
        AND (@CurrentInstance = @StandbyInstance OR @PrepareAll = 1) THEN 
        N'STANDBY = N''''' + @StandbyLocation + @dbname + N'.standby''''' ELSE 
        N'NORECOVERY' END + N';'';';
 
    EXEC [master].sys.sp_executesql @sql;
 
    -- record the fact that we've restored logs
    INSERT dbo.PMAG_LogRestoreHistory
      (DatabaseName, ServerInstance, BackupSetID, RestoreTime)
    SELECT @dbname, @CurrentInstance, @BackupSetID, SYSDATETIME();
 
    -- mark the new standby
    IF @rn = 1 AND @CurrentInstance = @StandbyInstance -- this is the new STANDBY
    BEGIN
        UPDATE dbo.PMAG_Secondaries 
          SET IsCurrentStandby = CASE ServerInstance
            WHEN @StandbyInstance THEN 1 ELSE 0 END 
          WHERE DatabaseName = @dbname;
    END
 
    FETCH c INTO @BackupSetID, @CurrentInstance, @Location, @StandbyLocation, @rn;
  END
 
  CLOSE c; DEALLOCATE c;
END
```
13. selanjutnya adalah membuat SP untuk mendapatkan daftar backup instance yang aktif (memiliki data paling up to date, dibanding backup instance lain)
```
CREATE OR ALTER PROCEDURE dbo.PMAG_CleanupHistory
  @dbname   SYSNAME,
  @DaysOld  INT = 7
AS
BEGIN
  SET NOCOUNT ON;
 
  DECLARE @cutoff INT;
 
  -- this assumes that a log backup either 
  -- succeeded or failed on all secondaries 
  SELECT @cutoff = MAX(BackupSetID)
    FROM dbo.PMAG_LogBackupHistory AS bh
    WHERE DatabaseName = @dbname
    AND BackupTime < DATEADD(DAY, -@DaysOld, SYSDATETIME())
    AND EXISTS
    (
      SELECT 1 
        FROM dbo.PMAG_LogRestoreHistory AS rh
        WHERE BackupSetID = bh.BackupSetID
          AND DatabaseName = @dbname
          AND ServerInstance = bh.ServerInstance
    );
 
  DELETE dbo.PMAG_LogRestoreHistory
    WHERE DatabaseName = @dbname
    AND BackupSetID <= @cutoff;
 
  DELETE dbo.PMAG_LogBackupHistory 
    WHERE DatabaseName = @dbname
    AND BackupSetID <= @cutoff;
END
```
15. SP yang terakhir adalah untuk memudahkan proses penghapusan history backup
```
CREATE OR ALTER PROCEDURE dbo.PMAG_GetActiveSecondary
  @dbname SYSNAME
AS
BEGIN
  SET NOCOUNT ON;
 
  SELECT ServerInstance
    FROM dbo.PMAG_ActiveSecondaries
    WHERE DatabaseName = @dbname;
END
```
16. Untuk mempermudah monitoring dari proses log shipping maka dibuat view, view berikut digunakan untuk melihat backup yang berhasil dibuat
```
CREATE OR ALTER VIEW [dbo].[PMAG_BackupRestoreReport] AS SELECT
	b.BackupSetID as [ID],
	b.DatabaseName as [Database],
	b.ServerInstance as [Backup Server],
	b.BackupTime as [Backup Time],
	CONVERT(DATE, b.BackupTime) as [Backup Date],
	b.Location as [File Location],
	DATEDIFF(millisecond, b.BackupTime, r.RestoreTime) as [Duration (millisecond)]
FROM dbo.PMAG_LogBackupHistory b
	JOIN dbo.PMAG_LogRestoreHistory r ON b.BackupSetID=r.BackupSetID AND b.ServerInstance= r.ServerInstance AND b.DatabaseName= r.DatabaseName
```
view berikut ini digunakan untuk melihat backup yang gagal ter restore.
```
CREATE OR ALTER VIEW [dbo].[PMAG_FailBackupRestoreReport] AS 
SELECT
	b.BackupSetID as [ID],
	b.DatabaseName as [Database],
	b.ServerInstance as [Backup Server],
	b.BackupTime as [Backup Time],
	CONVERT(DATE, b.BackupTime) as [Backup Date],
	b.Location as [File Location],
	DATEDIFF(millisecond, b.BackupTime, r.RestoreTime) as [Duration (millisecond)]
FROM dbo.PMAG_LogBackupHistory b
	FULL OUTER JOIN dbo.PMAG_LogRestoreHistory r ON b.BackupSetID=r.BackupSetID AND b.ServerInstance= r.ServerInstance AND b.DatabaseName= r.DatabaseName
WHERE b.BackupSetID IS NULL OR r.BackupSetID IS NULL;
```
17. view terakhir adalah untuk melihat backup instance mana yang sedang aktif (memiliki data paling up to date dibanding backup instece lain)
```
CREATE OR ALTER VIEW dbo.PMAG_ActiveSecondaries
AS
  SELECT DatabaseName, ServerInstance
    FROM dbo.PMAG_Secondaries
    WHERE IsCurrentStandby = 1;
```
18. selanjutnya adalah memilih database yang akan dibackup, contohnya seperti database `LSDB` itu sendiri
```
USE LSDB;
GO
INSERT dbo.PMAG_Databases(DatabaseName) SELECT N'LSDB';
```
19. selanjutnya adalah memilih backup instance untuk db `LSDB` yaitu `localhost\SQLLS1` dan `localhost\SQLLS2`. Setiap instance memiliki _DataFolder_ dan _LogFolder_ masing-masing umumnya pada `C:\Program Files\Microsoft SQL Server\MSSQL15.{nama instance}\MSSQL\DATA\` untuk itu dapat dipastikan ulang lewat file explorer apakah folder tersebut ada. Untuk folder backup dam standby dari tiap backup instance adalah `D:\SQLLS1\` dan  `D:\SQLLS2\`.
```
INSERT dbo.PMAG_Secondaries
(
  DatabaseName,
  ServerInstance, 
  CommonFolder, 
  DataFolder, 
  LogFolder, 
  StandByLocation
)
SELECT 
  DatabaseName = N'LSDB', 
  ServerInstance = name,
  CommonFolder = 'D:\SQLLS' + RIGHT(name, 1) + '\', 
  DataFolder = 'C:\Program Files\Microsoft SQL Server\MSSQL15.SQLLS'  
               + RIGHT(name, 1) + '\MSSQL\DATA\',
  LogFolder  = 'C:\Program Files\Microsoft SQL Server\MSSQL15.SQLLS' 
               + RIGHT(name, 1) + '\MSSQL\DATA\',
  StandByLocation = 'D:\SQLLS' + RIGHT(name, 1) + '\' 
FROM sys.servers 
WHERE name LIKE N'.\SQLLS[1-2]';
```
jika tidak yakin dimana lokasi DataFolder dan LogFolder dari instance maste, maka bisa dicek dengan query berikut
```
SELECT 
    mdf.database_id, 
    mdf.name, 
    mdf.physical_name as data_file, 
    ldf.physical_name as log_file, 
    db_size = CAST((mdf.size * 8.0)/1024 AS DECIMAL(8,2)), 
    log_size = CAST((ldf.size * 8.0 / 1024) AS DECIMAL(8,2))
FROM (SELECT * FROM sys.master_files WHERE type_desc = 'ROWS' ) mdf
JOIN (SELECT * FROM sys.master_files WHERE type_desc = 'LOG' ) ldf
ON mdf.database_id = ldf.database_id
```
20. setelah selesai, maka initial backup untuk `LSDB` dapat dilakukan dengan mengeksekusi SP `PMAG_Backup` dengan parameter `type = bak` dan `init = 1`
```
EXEC dbo.PMAG_Backup @dbname = N'LSDB', @type = 'bak', @init = 1;
```
21. jika berhasil, dapat dicoba untuk melakukan log backup dengan SP yang sama namun dengan parameter  `type = trn` 
```
EXEC dbo.PMAG_Backup @dbname = N'LSDB', @type = 'trn';
```
22. jika semua lancar, maka otomasi dapat dilakukan dengan **Task Scheduler**
```
```
23. setelah memastikan setiap task sukses berjalan dengan otomatis, selanjutnya membuat document pada collections `lsdb` yang menampung credentials dari **master instance** yaitu `localhost\SQLDEV` dengan db `LSDB` dengan terminal run command berikut untuk masuk ke mongodb shell
```
-> mongo
```
lalu membuat document dalam collections `lsdb` pada database `logshipping` dengan perintah
```
> use logshipping
> db.lsdb.insertMany([
  {
    "drive" : "SQL Server",
    "server" : "localhost",
    "instance_name" : "SQLDEV",
    "ls_database" : "LSDB",
    "trusted_connection" : "yes"
  }])
```
24. setelah  maka sekarang waktunya run webserver untuk monitoring. Pastikan file `webserver.py` terdownload dan `requirements.txt` berhasil terinstall, lalu run command dibawah pada terminal dan jangan ditutup dan buka url yang tertera di terminal
```
-> streamlit run webserver.py
```
25. maka akan terdapat pesan error karena masih belum terhubung ke mongodb, maka harus membuat file `secrets.toml` dalam folder `.streamlit/` yang berada pada root directory python environment yang digunakan, berikut isi dari file `.streamlit/secrets.toml`, untuk lebih lengkap dapat dilihat pada https://docs.streamlit.io/knowledge-base/tutorials/databases/mongodb
```
# .streamlit/secrets.toml

[mongo]
host = "localhost"
port = 27017
username = "xxx"  # if using password
password = "xxx"
```
26. refresh web app, dan custom log shipping selesai terpasang

![alt text](https://raw.githubusercontent.com/hamzahmhmmd/CustomLogShippingSQLserver/master/images/Custom%20log%20shipping%20webapp.png?token=ALAAYUHLDKCCDU7Z6Y5EMP3BUXIMW "Custom Log Shipping Web App")

## Cara Penggunaan Web App

## Ucapan terimakasih
- https://sqlperformance.com/2014/10/sql-performance/readable-secondaries-on-a-budget karena telah berbaik hati membagikan sourcode yang menjadi dasar pengembangan projek ini
- https://streamlit.io karena project streamlit memudahkan pengmbangan web app pada projek ini
