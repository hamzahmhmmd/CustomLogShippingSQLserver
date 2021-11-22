@REM this command execute SP that delete backup and restore hitory of LSDB database when the data has 7 days old
sqlcmd -S .\SQLDEV -d LSDB -E -Q "EXEC dbo.PMAG_CleanupHistory @dbname = N'LSDB', @DaysOld = 7;"

@REM this command remove the log backup file that live in every backup instance common folder
forfiles /p D:\SQLLS1\ /S /M LSDB*.trn* /D -7 /C "cmd /c del @path"
forfiles /p D:\SQLLS2\ /S /M LSDB*.trn* /D -7 /C "cmd /c del @path"
